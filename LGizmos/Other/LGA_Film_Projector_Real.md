## LGA_Film_Projector_Real (Notas)

### Proposito
- Simula obturacion de proyector (3 palas) sobre un clip: muestra frame A, obtura 3 veces dentro del mismo ciclo, luego pasa a frame B.
- No mueve la imagen de origen; solo una tarjeta negra animada (ShutterCard → ShutterMove) tapa/destapa.

### Parametros principales
- `start_frame`: frame inicial del clip.
- `speed`: multiplicador de avance del clip. Ciclo = `1 / speed` frames de timeline por cada frame de origen.
- `frame_height`: altura usada para desplazar el obturador (tambien se toma del input con knobs internos si lo preferís).
- `motion_blur`, `shutter`: se pasan al Transform del obturador.

### Nodos clave
- `HoldA` / `HoldB`: samples consecutivos del input (A y B).
- `FrameSwitch`: conmuta a B al final del ciclo (despues de la tercera obturacion).
- `ShutterCard`: tarjeta negra.
- `ShutterMove`: transforma la tarjeta negra segun `NoOp1.shutter_y`.
- `NoOp1`: panel de debug y calculo de fases.

### Debug / calculos en NoOp1
- `cycle = 1 / max(speed, 0.0001)`
- `spacing = cycle / 3` (tres obturaciones por ciclo)
- Fases de cada obturacion (porcentaje de un tercio, modelo 60/10/20/10):
  - `down_len = spacing * 0.10`
  - `black_len = spacing * 0.20`
  - `up_len = spacing * 0.10`
  - visible restante ≈ 60% del tercio
- `phase_offset`: offset libre (frames de timeline) para desplazar la fase. Por defecto 0.
- `phase = (((frame - start_frame) + phase_offset + down_len + black_len*0.5) % cycle + cycle) % cycle`  
  (esto coloca el inicio del ciclo en el centro del tramo negro del primer tercio; con `phase_offset`=0, el frame de cambio cae en full black y es independiente de la velocidad)
- `ph = phase % spacing`
- `shutter_y`:
  - `ph < down_len` → interpola de `-frame_height` a `0` (baja desde arriba)
  - `ph < down_len + black_len` → `0` (tapado)
  - `ph < down_len + black_len + up_len` → interpola de `0` a `+frame_height` (sigue bajando, destapa por abajo)
  - resto → `+frame_height` (fuera de cuadro por abajo)
- `blackout`: valor 0..1 de porcentaje de negro visible (0 imagen limpia, 1 negro).
- `image_level`: valor 0..1 de porcentaje de imagen visible (1 imagen limpia, 0 negro). Es el complementario suavizado.
- UI: `Black Level (0-1)` expone `NoOp1.image_level` (1 = full imagen, 0 = full negro) en el panel principal del gizmo para reutilizarlo al animar otros efectos.

### Conexion
- `ShutterMove.translate.y = NoOp1.shutter_y`
- `FrameSwitch.which = NoOp1.phase >= (2*spacing + down_len + black_len + up_len)` (despues de 3 obturaciones)

### Notas de uso
- Con `speed=0.02`, ciclo=50 f: en frame 1001 el obturador esta arriba (`shutter_y` negativo) y deberia bajar; si entra/sale demasiado pronto, ajusta `phase_offset` (se suma a la fase antes del modulo, escala con el ciclo). Valores positivos retrasan la entrada.
- `frame_height` se puede fijar manual (default 480) o enlazar al input; centro del Transform usa el size del input.

### Reset rapido
- Si algo se desfaso, revisa en `NoOp1`:
  - `phase` debe estar en rango 0..cycle
  - `shutter_y` negativo al inicio del ciclo si quieres ver el tail saliendo en el primer frame.

