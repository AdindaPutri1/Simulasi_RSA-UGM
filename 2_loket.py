import pygame
import sys
import random
import time
import csv  # Tambahkan pustaka csv untuk menyimpan data

# Inisialisasi pygame
pygame.init()

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Ukuran layar
WIDTH, HEIGHT = 1250, 600
SCREEN_SIZE = (WIDTH, HEIGHT)

# Posisi
POS_LOKET_PENDAFTARAN_1 = (50, 70)
POS_LOKET_PENDAFTARAN_2 = (200, 70)
POS_RUANG_TUNGGU = (50, 400)
POS_RUANG_PEMERIKSAAN = (500, 70)
POS_IGD = (800, 70)
START_POS = (0, HEIGHT - 50)

# Kecepatan awal
SPEED = 2
SPEED_FACTOR = 1
TIME_FACTOR = 1

# Setup layar
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Simulasi Antrian Pasien dengan Dua Loket")

# Fungsi untuk menggambar teks
def draw_text(text, position, font_size=36, color=BLACK):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

# Fungsi untuk memindahkan pasien
def move_patient(patient, target, speed):
    dx = target[0] - patient['x']
    dy = target[1] - patient['y']
    dist = (dx**2 + dy**2)**0.5

    if dist != 0:
        move_x = speed * dx / dist
        move_y = speed * dy / dist
        if abs(move_x) > abs(dx):
            move_x = dx
        if abs(move_y) > abs(dy):
            move_y = dy

        patient['x'] += move_x
        patient['y'] += move_y

# Fungsi untuk menghitung posisi antrian mengular
def calculate_snake_position(index, start_pos, row_length, spacing):
    row = index // row_length
    col = index % row_length
    if row % 2 == 0:
        x = start_pos[0] + col * spacing
    else:
        x = start_pos[0] + (row_length - 1 - col) * spacing
    y = start_pos[1] + row * spacing
    return (x, y)

# Main loop
def main():
    global SPEED, SPEED_FACTOR, TIME_FACTOR
    clock = pygame.time.Clock()
    running = True

    # Daftar pasien
    patients = [
        {'color': RED, 'x': START_POS[0], 'y': START_POS[1], 'target': POS_IGD}
    ]

    # Counters for patients
    count_red = 1
    count_yellow = 0
    count_green = 0
    total_patients = 1

    # Status antrian
    loket_empty_1 = True
    loket_empty_2 = True
    waiting_queue = []
    waiting_times = {}
    current_patient_at_loket_1 = None
    current_patient_at_loket_2 = None
    time_at_loket_end_1 = 0
    time_at_loket_end_2 = 0

    # Start time for day change
    start_time = time.time()
    day = 1

    # Data for CSV
    daily_patient_data = []

    # Track new patients each day
    new_patients_today = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Simpan data ke file CSV sebelum keluar
                with open('patient_data.csv', mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Day', 'New Patients'])
                    for entry in daily_patient_data:
                        writer.writerow(entry)
                
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    SPEED_FACTOR = min(SPEED_FACTOR + 0.1, 10.0)  # Batasi faktor kecepatan maksimum
                elif event.key == pygame.K_DOWN:
                    SPEED_FACTOR = max(SPEED_FACTOR - 0.1, 0.1)  # Batasi faktor kecepatan minimum

        # Check for day change every 4 minutes (240 seconds)
        elapsed_time = time.time() - start_time
        if elapsed_time > 240 / SPEED_FACTOR:  # 4 minutes in seconds adjusted by speed factor
            daily_patient_data.append((day, new_patients_today))  # Tambahkan data jumlah pasien baru per hari
            day += 1
            start_time = time.time()  # reset the start time
            new_patients_today = 0  # Reset new patients count for new day

        # Tambah pasien secara acak
        if random.randint(1, int(200 / SPEED_FACTOR)) <= 1:
            new_patient = {'color': RED, 'x': START_POS[0], 'y': START_POS[1], 'target': POS_IGD}
            patients.append(new_patient)
            count_red += 1
            total_patients += 1
            new_patients_today += 1
        elif random.randint(1, int(200 / SPEED_FACTOR)) <= 2:
            new_patient = {'color': GREEN, 'x': START_POS[0], 'y': START_POS[1], 'target': POS_RUANG_TUNGGU, 'waiting': False, 'wait_start': 0, 'wait_duration': 0}
            patients.append(new_patient)
            waiting_queue.append(new_patient)
            waiting_times[id(new_patient)] = pygame.time.get_ticks() + random.randint(2000, 5000)
            count_green += 1
            total_patients += 1
            new_patients_today += 1
        elif random.randint(1, int(200 / SPEED_FACTOR)) <= 1:
            new_patient = {'color': YELLOW, 'x': START_POS[0], 'y': START_POS[1], 'target': POS_RUANG_TUNGGU, 'waiting': False, 'wait_start': 0, 'wait_duration': 0}
            patients.append(new_patient)
            waiting_queue.append(new_patient)
            waiting_times[id(new_patient)] = pygame.time.get_ticks() + random.randint(2000, 5000)
            count_yellow += 1
            total_patients += 1
            new_patients_today += 1

        # Pindahkan pasien
        for patient in patients:
            if patient['color'] == RED:
                move_patient(patient, POS_IGD, SPEED * SPEED_FACTOR)
            elif patient['color'] in [YELLOW, GREEN]:
                if patient['waiting'] and pygame.time.get_ticks() - patient['wait_start'] < patient['wait_duration']:
                    continue  # Pasien masih menunggu di loket
                else:
                    move_patient(patient, patient['target'], SPEED * SPEED_FACTOR)

        # Update status loket
        if current_patient_at_loket_1 is None and waiting_queue:
            if pygame.time.get_ticks() >= waiting_times[id(waiting_queue[0])]:
                current_patient_at_loket_1 = waiting_queue.pop(0)
                current_patient_at_loket_1['target'] = POS_LOKET_PENDAFTARAN_1
                time_at_loket_end_1 = pygame.time.get_ticks() + (random.randint(2000, 5000) // SPEED_FACTOR)
                current_patient_at_loket_1['wait_start'] = pygame.time.get_ticks()
                del waiting_times[id(current_patient_at_loket_1)]

        if current_patient_at_loket_2 is None and waiting_queue:
            if pygame.time.get_ticks() >= waiting_times[id(waiting_queue[0])]:
                current_patient_at_loket_2 = waiting_queue.pop(0)
                current_patient_at_loket_2['target'] = POS_LOKET_PENDAFTARAN_2
                time_at_loket_end_2 = pygame.time.get_ticks() + (random.randint(2000, 5000) // SPEED_FACTOR)
                current_patient_at_loket_2['wait_start'] = pygame.time.get_ticks()
                del waiting_times[id(current_patient_at_loket_2)]

        if current_patient_at_loket_1:
            move_patient(current_patient_at_loket_1, POS_LOKET_PENDAFTARAN_1, SPEED * SPEED_FACTOR)

            if (current_patient_at_loket_1['x'] == POS_LOKET_PENDAFTARAN_1[0] and
                current_patient_at_loket_1['y'] == POS_LOKET_PENDAFTARAN_1[1]):
                if not current_patient_at_loket_1['waiting']:
                    current_patient_at_loket_1['waiting'] = True
                    current_patient_at_loket_1['wait_start'] = pygame.time.get_ticks()
                    current_patient_at_loket_1['wait_duration'] = (random.randint(2000, 5000) // SPEED_FACTOR)
                elif pygame.time.get_ticks() - current_patient_at_loket_1['wait_start'] >= current_patient_at_loket_1['wait_duration']:
                    if current_patient_at_loket_1['color'] == GREEN:
                        current_patient_at_loket_1['target'] = POS_RUANG_PEMERIKSAAN
                    else:
                        current_patient_at_loket_1['target'] = (-50, current_patient_at_loket_1['y'])  # Keluar layar ke kiri
                    current_patient_at_loket_1['waiting'] = False
                    current_patient_at_loket_1 = None

        if current_patient_at_loket_2:
            move_patient(current_patient_at_loket_2, POS_LOKET_PENDAFTARAN_2, SPEED * SPEED_FACTOR)

            if (current_patient_at_loket_2['x'] == POS_LOKET_PENDAFTARAN_2[0] and
                current_patient_at_loket_2['y'] == POS_LOKET_PENDAFTARAN_2[1]):
                if not current_patient_at_loket_2['waiting']:
                    current_patient_at_loket_2['waiting'] = True
                    current_patient_at_loket_2['wait_start'] = pygame.time.get_ticks()
                    current_patient_at_loket_2['wait_duration'] = (random.randint(2000, 5000) // SPEED_FACTOR)
                elif pygame.time.get_ticks() - current_patient_at_loket_2['wait_start'] >= current_patient_at_loket_2['wait_duration']:
                    if current_patient_at_loket_2['color'] == GREEN:
                        current_patient_at_loket_2['target'] = POS_RUANG_PEMERIKSAAN
                    else:
                        current_patient_at_loket_2['target'] = (-50, current_patient_at_loket_2['y'])  # Keluar layar ke kiri
                    current_patient_at_loket_2['waiting'] = False
                    current_patient_at_loket_2 = None

        # Update posisi antrian ruang tunggu
        row_length = 39
        spacing = 30
        for idx, patient in enumerate(waiting_queue):
            target_x, target_y = calculate_snake_position(idx, POS_RUANG_TUNGGU, row_length, spacing)
            if patient['target'] not in [POS_LOKET_PENDAFTARAN_1, POS_LOKET_PENDAFTARAN_2]:
                patient['target'] = (target_x, target_y)

        # Clear layar
        screen.fill(WHITE)

        # Gambar kotak ruangan
        pygame.draw.rect(screen, (200, 200, 200), (*POS_LOKET_PENDAFTARAN_1, 125, 50))
        pygame.draw.rect(screen, (200, 200, 200), (*POS_LOKET_PENDAFTARAN_2, 125, 50))
        pygame.draw.rect(screen, (200, 200, 200), (*POS_RUANG_TUNGGU, 1150, 200))
        pygame.draw.rect(screen, (200, 200, 200), (*POS_RUANG_PEMERIKSAAN, 275, 200))
        pygame.draw.rect(screen, (255, 0, 0), (*POS_IGD, 250, 200))

        # Gambar teks ruangan
        draw_text("Loket 1", (POS_LOKET_PENDAFTARAN_1[0], POS_LOKET_PENDAFTARAN_1[1] - 40))
        draw_text("Loket 2", (POS_LOKET_PENDAFTARAN_2[0], POS_LOKET_PENDAFTARAN_2[1] - 40))
        draw_text("Ruang Tunggu", (POS_RUANG_TUNGGU[0], POS_RUANG_TUNGGU[1] - 40))
        draw_text("Ruang Pemeriksaan", (POS_RUANG_PEMERIKSAAN[0], POS_RUANG_PEMERIKSAAN[1] - 40))
        draw_text("IGD", (POS_IGD[0], POS_IGD[1] - 40))

        # Gambar pasien
        for patient in patients:
            pygame.draw.circle(screen, patient['color'], (int(patient['x']), int(patient['y'])), 15)

        # Gambar keterangan jumlah pasien
        draw_text(f"Pasien Merah: {count_red}", (WIDTH - 150, 10), 22)
        draw_text(f"Pasien Kuning: {count_yellow}", (WIDTH - 150, 40), 22)
        draw_text(f"Pasien Hijau: {count_green}", (WIDTH - 150, 70), 22)
        draw_text(f"Total Pasien: {total_patients}", (WIDTH - 150, 100), 22)

        # Gambar keterangan hari
        draw_text(f"Hari ke-{day}", (WIDTH - 150, 130), 40, RED)

        # Update layar
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
