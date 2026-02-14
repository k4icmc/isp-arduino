===================================================
PROJETO: CONTROLE DE ARDUINO POR DETECÇÃO DE MÃOS
===================================================

DESCRIÇÃO:
Este projeto utiliza a câmera do notebook para detectar mãos,
contar dedos e controlar um Arduino que acende LEDs e move um
servo motor proporcionalmente ao número de dedos levantados.

===================================================
COMPONENTES NECESSÁRIOS:
===================================================
- 1 Arduino Uno (ou similar)
- 1 Servo motor
- 5 LEDs (cores variadas)
- 5 Resistores de 220Ω
- Fios jumpers
- Protoboard
- Notebook com câmera

===================================================
MONTAGEM DO CIRCUITO:
===================================================
Servo motor:
- Pino de sinal (laranja/amarelo) → Pino 9 do Arduino
- VCC (vermelho) → 5V do Arduino
- GND (marrom/preto) → GND do Arduino

LEDs (todos com resistor de 220Ω em série):
- LED 1 (ânodo) → Pino 3 do Arduino
- LED 2 (ânodo) → Pino 4 do Arduino
- LED 3 (ânodo) → Pino 5 do Arduino
- LED 4 (ânodo) → Pino 6 do Arduino
- LED 5 (ânodo) → Pino 7 do Arduino
- Todos os cátodos dos LEDs → GND do Arduino

===================================================
INSTALAÇÃO DAS BIBLIOTECAS (Python):
===================================================
Abra o terminal e execute:

pip uninstall mediapipe -y
pip install mediapipe==0.10.5
pip install opencv-python
pip install pyserial
pip install numpy

===================================================
PASSO A PASSO PARA EXECUTAR:
===================================================
1. Monte o circuito conforme diagrama acima
2. Conecte o Arduino ao notebook via USB
3. Abra o Arduino IDE
4. Carregue o arquivo 'controle_mao_arduino.ino' no Arduino
5. Anote a porta serial (ex: COM3, /dev/ttyUSB0)
6. No arquivo Python, altere a variável PORTA_ARDUINO
7. Execute o programa Python: python detectar_maos_arduino.py
8. Mostre sua mão para a câmera
9. Pressione 'q' para sair

===================================================
FUNCIONAMENTO:
===================================================
0 dedos → Todos LEDs apagados, servo em 0°
1 dedo  → LED 1 aceso, servo em ~34°
2 dedos → LEDs 1-2 acesos, servo em ~68°
3 dedos → LEDs 1-3 acesos, servo em ~102°
4 dedos → LEDs 1-4 acesos, servo em ~136°
5 dedos → Todos LEDs acesos, servo em ~170°

===================================================
SOLUÇÃO DE PROBLEMAS:
===================================================
Problema: "Não conecta ao Arduino"
Solução: Verifique a porta serial no código Python

Problema: "Câmera não abre"
Solução: Feche outros programas (Zoom, Teams, etc)

Problema: "Não detecta mãos"
Solução: Melhore a iluminação, evite fundo confuso

Problema: "LEDs não acendem"
Solução: Verifique polaridade e resistores

Problema: "Servo não move"
Solução: Verifique fiação e alimentação

===================================================
ARQUIVOS DO PROJETO:
===================================================
- instalar_bibliotecas.bat    → Instala as bibliotecas (Windows)
- controle_mao_arduino.ino    → Código do Arduino (C++)
- detectar_maos_arduino.py    → Código principal (Python)
- README.txt                   → Este arquivo de instruções

===================================================
Desenvolvido para projeto educacional
===================================================
