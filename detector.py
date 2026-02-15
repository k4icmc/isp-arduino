import cv2
import mediapipe as mp
import serial
import time
import numpy as np
import sys

# ============================================
# VERIFICA VERSÃO DO MEDIAPIPE E AJUSTA IMPORTS
# ============================================
print("="*50)
print("CONTROLE DE ARDUINO POR DETECÇÃO DE MÃOS")
print("="*50)

# Verifica versão do Python
print(f"\n🐍 Python versão: {sys.version[:5]}")

# Tenta importar o MediaPipe de diferentes formas
try:
    # Primeiro tenta o formato padrão
    import mediapipe as mp
    print(f"📦 MediaPipe versão: {mp.__version__}")
    
    # Verifica se 'solutions' existe diretamente
    if hasattr(mp, 'solutions'):
        print("✅ Usando formato: mp.solutions.hands")
        mp_maos = mp.solutions.hands
        mp_desenho = mp.solutions.drawing_utils
    else:
        # Se não existir, tenta o caminho alternativo
        print("🔄 Tentando formato alternativo...")
        from mediapipe.python.solutions import hands as mp_hands
        from mediapipe.python.solutions import drawing_utils as mp_drawing
        mp_maos = mp_hands
        mp_desenho = mp_drawing
        print("✅ Usando formato: from mediapipe.python.solutions import hands")
        
except Exception as e:
    print(f"❌ Erro ao importar MediaPipe: {e}")
    print("   Execute: pip install mediapipe==0.10.5")
    sys.exit(1)

# ============================================
# CONEXÃO COM ARDUINO
# ============================================
# MUDE AQUI PARA A PORTA DO SEU ARDUINO!
# No Windows: COM3, COM4, COM5 (veja no Arduino IDE)
# No Linux: /dev/ttyUSB0 ou /dev/ttyACM0
# No Mac: /dev/cu.usbmodem*

PORTA_ARDUINO = 'COM3'  # <---- MUDE AQUI!

print(f"\n🔌 Conectando ao Arduino na porta {PORTA_ARDUINO}...")

arduino_conectado = False
arduino = None

# Tenta conectar ao Arduino
try:
    arduino = serial.Serial(PORTA_ARDUINO, 9600, timeout=1)
    time.sleep(2)  # Aguarda o Arduino reiniciar
    print("✅ Arduino conectado com sucesso!")
    print("   LEDs e servo prontos para receber comandos")
    arduino_conectado = True
except Exception as e:
    print(f"❌ ERRO: Não foi possível conectar ao Arduino!")
    print(f"   Detalhes: {e}")
    print("   Verifique:")
    print("   1. Se o Arduino está conectado no USB")
    print("   2. Se a porta está correta (tente COM3, COM4, /dev/ttyUSB0, etc)")
    print("   3. Se o código já foi carregado no Arduino")
    print("\n⚠️ Continuando SEM Arduino (apenas teste de câmera)")
    arduino_conectado = False

# ============================================
# CONFIGURAÇÃO DA CÂMERA
# ============================================
print("\n📷 Iniciando câmera...")

# Tenta abrir a câmera (0 = câmera padrão do notebook)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ ERRO: Não foi possível abrir a câmera no índice 0!")
    print("   Tentando com índice 1...")
    cap = cv2.VideoCapture(1)
    
if not cap.isOpened():
    print("❌ ERRO: Nenhuma câmera encontrada!")
    print("   Verifique:")
    print("   1. Se a câmera do notebook está funcionando")
    print("   2. Se nenhum outro programa está usando a câmera (Zoom, Teams, etc)")
    print("   3. Se as permissões da câmera estão ativadas no Windows")
    sys.exit(1)

# Configura resolução
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
print("✅ Câmera iniciada com sucesso!")

# ============================================
# CONFIGURAÇÃO DO MEDIAPIPE (DETECÇÃO DE MÃOS)
# ============================================
print("\n🖐️ Inicializando detector de mãos...")

try:
    # Inicializa o detector de mãos
    maos = mp_maos.Hands(
        static_image_mode=False,      # Modo vídeo (processa frame a frame)
        max_num_hands=1,               # Detecta apenas 1 mão
        min_detection_confidence=0.7,  # Confiança mínima para detectar (70%)
        min_tracking_confidence=0.5    # Confiança para rastrear (50%)
    )
    print("✅ Detector de mãos inicializado!")
except Exception as e:
    print(f"❌ Erro ao inicializar detector de mãos: {e}")
    sys.exit(1)

# ============================================
# FUNÇÃO PARA CONTAR DEDOS
# ============================================
def contar_dedos(landmarks_mao):
    """
    Conta quantos dedos estão levantados
    Retorna: número de dedos (0 a 5)
    """
    dedos = 0
    
    # Índices das pontas dos dedos no MediaPipe
    # Polegar: 4, Indicador: 8, Médio: 12, Anelar: 16, Mínimo: 20
    pontas = [4, 8, 12, 16, 20]
    
    # POLEGAR - comparação no eixo X
    # Para mão direita: ponta do polegar mais à esquerda que a base = levantado
    try:
        if landmarks_mao.landmark[pontas[0]].x < landmarks_mao.landmark[pontas[0] - 1].x:
            dedos += 1
    except:
        pass  # Se der erro, ignora
    
    # OUTROS DEDOS - comparação no eixo Y
    # Ponta do dedo mais acima que a junta = levantado
    for i in range(1, 5):
        try:
            if landmarks_mao.landmark[pontas[i]].y < landmarks_mao.landmark[pontas[i] - 2].y:
                dedos += 1
        except:
            pass  # Se der erro, ignora
    
    return dedos

# ============================================
# FUNÇÃO PARA ENVIAR COMANDO AO ARDUINO
# ============================================
def enviar_comando_arduino(num_dedos):
    """
    Envia o número de dedos para o Arduino
    Formato: 100 + num_dedos (ex: 102 = 2 dedos)
    """
    if arduino_conectado and arduino and arduino.is_open:
        try:
            comando = f"{100 + num_dedos}\n"
            arduino.write(comando.encode())
            print(f"📤 Enviado para Arduino: {num_dedos} dedo(s)")
        except Exception as e:
            print(f"❌ Erro ao enviar comando: {e}")

# ============================================
# LOOP PRINCIPAL
# ============================================
print("\n" + "="*50)
print("🚀 SISTEMA INICIADO!")
print("="*50)
print("\n📋 INSTRUÇÕES:")
print("   • Mostre sua mão para a câmera")
print("   • Os LEDs vão acender conforme os dedos levantados")
print("   • O servo vai se mover proporcionalmente")
print("   • Pressione 'q' para sair")
print("   • Pressione 'c' para limpar o console")
print("="*50 + "\n")

# Variáveis de controle
ultimo_envio = 0
INTERVALO_ENVIO = 0.3  # Envia comando a cada 0.3 segundos (evita spam)
ultimos_dedos = -1  # Para não enviar repetido

# Contador de frames para estatísticas
frame_count = 0
start_time = time.time()

while True:
    # Captura frame da câmera
    sucesso, frame = cap.read()
    
    if not sucesso:
        print("❌ Erro ao capturar frame da câmera")
        break
    
    # Espelha a imagem (mais intuitivo)
    frame = cv2.flip(frame, 1)
    
    # Converte BGR para RGB (MediaPipe usa RGB)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Processa o frame para detectar mãos
    try:
        resultados = maos.process(frame_rgb)
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        continue
    
    # Converte de volta para BGR para exibição
    frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
    
    # Variável para armazenar número de dedos
    num_dedos = 0
    
    # Se detectou mãos
    if resultados.multi_hand_landmarks:
        for landmarks_mao in resultados.multi_hand_landmarks:
            # Desenha os pontos e conexões na mão
            try:
                mp_desenho.draw_landmarks(
                    frame, 
                    landmarks_mao, 
                    mp_maos.HAND_CONNECTIONS,
                    mp_desenho.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2),  # Azul para pontos
                    mp_desenho.DrawingSpec(color=(0, 255, 0), thickness=2)  # Verde para conexões
                )
            except:
                # Se falhar ao desenhar, tenta com parâmetros padrão
                mp_desenho.draw_landmarks(
                    frame, 
                    landmarks_mao, 
                    mp_maos.HAND_CONNECTIONS
                )
            
            # Conta os dedos
            num_dedos = contar_dedos(landmarks_mao)
            
            # Mostra contagem na tela
            texto_dedos = f"Dedos: {num_dedos}"
            cv2.putText(frame, texto_dedos, (10, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            
            # Envia comando para o Arduino (apenas se mudou o número de dedos)
            tempo_atual = time.time()
            if num_dedos != ultimos_dedos and tempo_atual - ultimo_envio > INTERVALO_ENVIO:
                enviar_comando_arduino(num_dedos)
                ultimo_envio = tempo_atual
                ultimos_dedos = num_dedos
            
            # Desenha um retângulo com a cor correspondente ao número de dedos
            cores = [
                (128, 128, 128),  # 0 dedos - Cinza
                (0, 255, 255),    # 1 dedo - Amarelo
                (255, 0, 255),    # 2 dedos - Magenta
                (255, 255, 0),    # 3 dedos - Ciano
                (0, 255, 0),      # 4 dedos - Verde
                (0, 0, 255)       # 5 dedos - Vermelho
            ]
            cv2.rectangle(frame, (10, 80), (200, 130), cores[num_dedos], -1)
            
    else:
        # Se não detectou mão
        cv2.putText(frame, "Nenhuma mao detectada", (10, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Se perdeu a mão, envia comando 0 dedos (apenas uma vez)
        if ultimos_dedos != 0:
            enviar_comando_arduino(0)
            ultimos_dedos = 0
    
    # Mostra status da conexão Arduino
    if arduino_conectado:
        status_arduino = "✅ Arduino Conectado"
        cor_status = (0, 255, 0)
    else:
        status_arduino = "❌ Arduino Desconectado"
        cor_status = (0, 0, 255)
    
    cv2.putText(frame, status_arduino, (10, frame.shape[0] - 50), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, cor_status, 2)
    
    # Mostra instruções na tela
    cv2.putText(frame, "'q' para sair | 'c' limpar console", (10, frame.shape[0] - 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Mostra FPS
    frame_count += 1
    if time.time() - start_time >= 1:
        fps = frame_count
        frame_count = 0
        start_time = time.time()
    else:
        fps = "calculando..."
    
    cv2.putText(frame, f"FPS: {fps if isinstance(fps, str) else fps}", 
               (frame.shape[1] - 100, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Mostra o frame
    cv2.imshow('Controle Arduino por Detecção de Mãos', frame)
    
    # Processa teclas pressionadas
    tecla = cv2.waitKey(1) & 0xFF
    
    if tecla == ord('q'):
        print("\n👋 Encerrando programa...")
        break
    elif tecla == ord('c'):
        # Limpa o console
        print("\033c", end="")
        print("="*50)
        print("CONTROLE DE ARDUINO POR DETECÇÃO DE MÃOS")
        print("="*50)
        print("\n📋 Console limpo!")

# ============================================
# FINALIZAÇÃO
# ============================================
print("\n⏏️ Finalizando...")

# Desliga todos os LEDs e centraliza servo antes de sair
if arduino_conectado and arduino:
    print("📤 Enviando comando de desligamento para o Arduino...")
    enviar_comando_arduino(0)
    time.sleep(0.5)  # Aguarda o comando ser processado

# Libera recursos
cap.release()
cv2.destroyAllWindows()

if arduino_conectado and arduino:
    arduino.close()
    print("✅ Conexão com Arduino fechada")

print("✅ Programa finalizado com sucesso!")
print("="*50)
