> **Regla de documentacion**: este archivo describe el estado actual del codigo. No es un historial de cambios, changelog ni bitacora temporal.
> **Regla de documentacion**: este archivo debe incluir una seccion de referencias tecnicas con rutas completas a los archivos mas importantes relacionados, y para cada archivo nombrar las funciones, clases o metodos clave vinculados a este tema.

# LGA_BouncePos

Gizmo (grupo `.nk`, no `Gizmo`, editable por dentro) que genera un **rebote de posición procedural** a partir de la *aceleración* de un movimiento de origen (`Source Translate`). El único propósito del nodo es calcular un **offset (x, y) en píxeles** — expuesto en el knob `Bounce Offset` — que se linkea al `translate` (u otro knob) de otro nodo para que "rebote" cuando el movimiento de origen cambia bruscamente.

El nodo normalmente **no se conecta al stream de imagen**: se pega suelto y se usa solo su valor de offset por expresión.

## Idea de funcionamiento

1. Se toma un movimiento de origen (`Source Translate`), animado a mano o linkeado desde un Tracker/Transform.
2. Se calcula su **segunda diferencia** (≈ aceleración): un cambio repentino de velocidad produce un pico. Eso es el "golpe" que dispara el rebote.
3. Ese impulso se convierte en offset. Opcionalmente se le agrega una **cola oscilante amortiguada** (como un resorte que se asienta): controles `Bounce Length / Decay / Frequency`.
4. El resultado se suaviza (`Bounce Smooth`), se clampea (`Max Offset`) y queda disponible en `Bounce Offset`.

## Fórmulas

Notación por eje (x o y). `T(m)` = `Source Translate` en el frame `m`.

- **Lookahead**: `L = max(lookahead, 1)` — mitad del ancho de la ventana de muestreo.
- **Delay efectivo** (base + drift aleatorio suave), calculado en el nodo `Delay_Output`:
  ```
  d(f) = delay + delay_random_amount * noise((f + delay_random_seed) * delay_random_frequency)
  ```
  `noise()` es el ruido suave (Perlin) de Nuke, determinístico por seed. Con `delay_random_amount = 0` queda `d = delay`.
- **Impulso** (segunda diferencia central, negada y normalizada = aceleración):
  ```
  impulse(m) = -( T(m-d-L) - 2*T(m-d) + T(m-d+L) ) / (L*L)
  ```
- **Gate de start frame** (evita rebote falso al inicio del plano):
  ```
  gate(m) = (!ignore_start_frame) || ( (m-d-L) >= start_frame )
  ```
- **Impulso "crudo" gateado** (lo que calcula `Bounce_Impulse.g`, SIN amount/mult):
  ```
  G(m) = impulse(m) * gate(m) * impulse_weight(m)
  ```
- **Envolvente de la cola** (coeficientes `Bounce_Env.e1..e15`, dependen solo de los controles, no del frame):
  ```
  E_k = pow(max(1-bounce_decay, 0), k) * cos(2*pi * bounce_frequency * k / max(bounce_length, 1))
  ```
- **Offset crudo** (nodo `Bounce_Raw.bounce_raw`) = base + cola, escalado y clampeado:
  ```
  bounce_raw(f) = clamp(
      amount * axisMult * ( G(f) + SUM_{k=1..15} [ (bounce_length >= k) ? G(f-k) * E_k : 0 ] ),
      -max_offset, +max_offset )
  ```
  El término base `G(f)` es la respuesta instantánea (equivalente a la versión más simple del nodo). Cada término de cola `G(f-k)*E_k` es el mismo impulso de un frame anterior, atenuado por la envolvente.
- **Suavizado** (`Bounce_Transform.translate`), promedio de 3 frames mezclado por peso `w = min(bounce_smooth/5, 1)`:
  ```
  bounce_smooth<=0 : offset(f) = bounce_raw(f)
  bounce_smooth>0  : offset(f) = bounce_raw(f)*(1-w) + ((bounce_raw(f-1)+bounce_raw(f)+bounce_raw(f+1))/3)*w
  ```
- **Salida**: `bounce_offset = ( offset.x , offset.y )`.

## Controles expuestos (tab BouncePos)

- **Source Translate** — el movimiento del que se calcula el rebote. Animar acá o linkear de otro Transform/Tracker.
- **Lookahead** — ancho de la ventana de muestreo. Alto = reacciona a cambios de movimiento amplios; bajo = a cambios frame a frame más filosos.
- **Amount** — fuerza global. 0 desactiva; negativo invierte.
- **X Mult / Y Mult** — multiplicadores por eje.
- **Delay** — desfase base en frames (positivo usa movimiento anterior; negativo anticipa).
- **Delay Random Amount / Frequency / Seed** — variación aleatoria suave del delay (drift orgánico). `Amount = 0` la desactiva. `Frequency` = velocidad del drift. `Seed` = semilla para que setups gemelos deriven distinto.
- **Effective Delay** *(readout)* — el delay actual ya con el random sumado (`Delay_Output.effective_delay`).
- **Bounce Length** — largo de la cola en frames. 0 = solo respuesta instantánea (sin cola).
- **Bounce Decay** — qué tan rápido se apaga la cola. 0 = más energía; 1 = la mata casi al toque.
- **Bounce Frequency** — cantidad de ciclos de oscilación a lo largo de la cola.
- **Bounce Smooth** — suaviza el offset final sobre frames vecinos (no toca el movimiento de origen).
- **Start Frame / Ignore Start Frame** — primer frame válido del movimiento; evita rebote falso al inicio.
- **Impulse Weight** — multiplicador por frame del impulso. Animar a 0 en frames de tracking malo para que no alimenten la cola.
- **Max Offset** — clamp del offset generado por eje (px).
- **Bounce Offset** *(readout / punto de link)* — el offset final. Ver "Cómo linkear".

## Arquitectura interna (por qué está partido en nodos)

El grafo interno está deliberadamente **fragmentado en expresiones chicas**. Ninguna expresión de knob supera ~1–2 KB. Esto es una decisión de performance crítica (ver "Lecciones").

| Nodo | Rol | Expresión clave |
|---|---|---|
| `Input1` / `Output1` | Passthrough. El nodo no procesa imagen; su producto es el valor. | — |
| `Delay_Output` | Calcula el **delay efectivo** una vez por frame. | `effective_delay = delay + delay_random_amount*noise(...)` |
| `Bounce_Impulse` | Calcula el **impulso gateado de UN frame** `G(frame)`, SIN amount/mult. Se lee en `frame-k` para armar la cola barato. | `g` (xy) |
| `Bounce_Env` | Precalcula los **15 coeficientes de envolvente** `E_1..E_15` (invariantes en el tiempo). | `e1 … e15` |
| `Bounce_Raw` | La **suma corta** de la convolución: `G(frame-k) * E_k`, aplica amount/mult y clampea. | `bounce_raw` (xy) |
| `Bounce_Transform` | Aplica el **Bounce Smooth** sobre el offset final. | `translate` (xy) |
| `Bounce_Output` | Espeja el offset suavizado en `bounce_offset` para linkear desde afuera. | `bounce_offset` (xy) |

**El truco central**: en vez de desenrollar la convolución (repetir el cálculo del impulso 16 veces por eje inline), `Bounce_Raw` lee `Bounce_Impulse.g(frame-k)`. Al leer un knob-expresión en un tiempo desplazado, Nuke evalúa toda la expresión con `frame := (frame-k)`, así que `translate`, `impulse_weight`, el gate y el `effective_delay` se desplazan solos y **reproducen exactamente el tap k** — con una expresión chiquita en vez de una gigante.

## Cómo linkear el offset a otro nodo

El offset vive en el knob `Bounce Offset` (y en `Bounce_Output.bounce_offset`).

- **Método 1 (copy/paste link)**: click derecho en `Bounce Offset` → *Copy*; en el nodo destino, click derecho en el knob (ej. `translate`) → *Paste absolute*.
- **Método 2 (expresión)**: en el knob destino → *Add expression* (`=`) y escribir:
  ```
  <NombreDelNodo>.bounce_offset.x      (campo X)
  <NombreDelNodo>.bounce_offset.y      (campo Y)
  ```
  Ej.: `LGA_BouncePos1.bounce_offset.x`. Reemplazar `LGA_BouncePos1` por el nombre real de la instancia pegada.

## Lecciones / trampas de performance (causas reales)

Conocimiento reutilizable extraído de depurar un lag severo del nodo. Se documenta acá porque **explica por qué el nodo está armado como está**.

### Lección 1 — El costo de UI de una expresión escala con su TAMAÑO, no con lo que ejecuta

**Síntoma**: con solo pegar el nodo y **abrir su panel** (desconectado, sin viewer, sin hacer nada), cualquier acción en todo el script se volvía ~1 segundo más lenta.

**Lo que sospechamos mal** (y por qué era falso):
- *El readout `Bounce Offset`* → se sacó y el lag siguió.
- *Los knobs link `filter/motionblur/shutter`* → contribuían, pero no eran la causa de fondo.
- *El delay random / las muestras de smooth* → se habían quitado en versiones previas sin resolver nada.
- *El modo de re-evaluación "Always"* → ya estaba en **Lazy**.
- *La cantidad de taps ejecutados* → poner `Bounce Length = 0` (que cortocircuita los 15 taps) **no cambiaba el lag**. Esto fue la prueba definitiva: no era la ejecución.

**Causa real**: la expresión de `bounce_raw` había crecido a ~17.000 caracteres (15 taps × segunda diferencia completa × 2 ejes, desenrollados inline, + 30 `pow` + 30 `cos`). Con el panel abierto, Nuke **recorre/rehashea todo el árbol parseado de esa expresión en cada redibujo del DAG** (fase *store* + descubrimiento de dependencias en modo Lazy + hashing), **independientemente de qué rama del ternario se ejecute**. La v0.2 (expresión de 615 chars) nunca lageó; la diferencia era puramente el tamaño.

**Solución**: partir el cálculo en nodos internos para que **ninguna expresión sea grande** (`Bounce_Impulse` ~600, `Bounce_Env` triviales, `Bounce_Raw` ~1.200/eje). La expresión más grande bajó de ~17.000 a ~2.500 chars (7× más chica) → lag eliminado, resultado idéntico.

### Lección 2 — El ternario NO ahorra costo de UI

`(cond) ? (cálculo pesado) : 0` cortocircuita la **ejecución**, pero el árbol parseado igual **contiene** el cálculo pesado. El costo de parseo/dependencias/hash se paga exista o no la ejecución. (Por eso `Bounce Length = 0` no ayudaba.) El ternario sirve para el playback/render, no para la fluidez del panel.

### Lección 3 — Leer un knob-expresión en tiempo desplazado desplaza TODO lo de adentro

`Node.knob(frame-k)` evalúa la expresión entera con `frame := (frame-k)`. Toda referencia sin argumento de tiempo adentro se desplaza también. Consecuencias de diseño:
- `amount`, `x_mult`, `y_mult` se **factorizan afuera** de `Bounce_Impulse` (se aplican en `Bounce_Raw` al frame actual), para que se lean al frame de salida y no al del tap. Así el resultado es idéntico incluso si se anima `amount`.
- Adentro de `Bounce_Impulse.g` van solo las cosas que **deben** desplazarse por tap: `Source Translate`, `impulse_weight` y el `effective_delay`.
- **No conviene animar** `delay`, `lookahead`, `start_frame`, `ignore_start_frame`: se desplazarían junto con la cola (leerían el valor de `frame-k`, no el actual). Se pueden animar sin problema: `amount`, `x_mult`, `y_mult`, `impulse_weight`, `bounce_decay/frequency/length`, `delay_random_*`.

### Lección 4 — Nuke no memoiza lecturas de expresión

No hay caché de `knob(t)`: leer el mismo valor N veces = N evaluaciones. Por eso partir en un nodo intermedio **no reduce la cantidad de evaluaciones ni las lecturas** (el nodo se re-evalúa en cada tap). **Sí** reduce el **tamaño** de cada expresión, que es el costo de UI (Lección 1). Son dos problemas distintos: el split ataca el tamaño, no la ejecución.

### Lección 5 — Los readouts vivos y los labels `[value ...]` cuestan en cada redraw

Un readout que muestra un valor pesado (o un `label` con `[value ...]`) fuerza a evaluar esa cadena en cada refresco del panel. Con expresiones chicas es imperceptible; con expresiones grandes, es parte del lag. El panel abierto es lo que "pinnea" toda la cadena en el loop de refresco: cerrar el panel cuando no se usa también ayuda.

### Lección 6 — La versión chica no era "mejor", era chica

La versión temprana no lageaba porque hacía casi nada (solo el impulso instantáneo). La cola de rebote es genuinamente más cálculo. La clave no fue **quitar** features, sino mantener **cada expresión chica**. Con eso se pudo reintegrar todo (cola, delay random, etc.) sin lag.

## Reglas para no romper la performance

- Mantener **cada expresión de knob chica** (≲ 1–2 KB). Si crece, partir en nodos internos.
- **No desenrollar convoluciones inline**: usar un nodo "impulso por frame" + lectura en `frame-k`.
- **Precalcular** lo invariante en el tiempo (envolvente) en knobs aparte.
- **Factorizar afuera** del nodo time-shifted lo que debe leerse al frame actual (`amount`, mults).
- No animar `delay / lookahead / start_frame / ignore_start_frame` (ver Lección 3).
- Tener **Expression Re-Evaluation Mode = Lazy** (Preferences → Performance → Expressions).
- Cerrar el panel del nodo cuando no se usa.

## Referencias técnicas

- **`C:\Users\leg4-pc\.nuke\LGA_NodePack\LGizmos\Distort\LGA_BouncePos.nk`** — el gizmo. Nodos internos y knobs/expresiones clave:
  - `Delay_Output.effective_delay` — delay base + drift aleatorio suave (`noise`).
  - `Bounce_Impulse.g` (xy) — impulso gateado de un frame `G(frame)` (2ª diferencia · gate · `impulse_weight`), sin amount/mult; se muestrea en `frame-k`.
  - `Bounce_Env.e1 … e15` — coeficientes de envolvente `E_k = pow(max(1-decay,0),k)·cos(2π·freq·k/max(length,1))`.
  - `Bounce_Raw.bounce_raw` (xy) — suma de la convolución `amount·mult·(G(f)+Σ (length≥k)?G(f-k)·E_k:0)`, clampeada a ±`max_offset`.
  - `Bounce_Transform.translate` (xy) — Bounce Smooth (mezcla del offset con su promedio de 3 frames).
  - `Bounce_Output.bounce_offset` (xy) — espejo del offset final; fuente del link externo.
  - Knob del grupo para linkear: `<instancia>.bounce_offset.x` / `.y` (ej. `LGA_BouncePos1.bounce_offset`).

## Ubicación

`C:\Users\leg4-pc\.nuke\LGA_NodePack\LGizmos\Distort\LGA_BouncePos.nk`
