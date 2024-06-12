import matplotlib.pyplot as plt
import csv

# Baca data dari file CSV
days = []
new_patients = []

with open('patient_data.csv', mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        days.append(int(row['Day']))
        new_patients.append(int(row['New Patients']))

# Plot data
plt.figure(figsize=(10, 5))
plt.plot(days, new_patients, marker='o')
plt.title('Jumlah Pasien Baru per Hari')
plt.xlabel('Hari')
plt.ylabel('Jumlah Pasien Baru')
plt.grid(True)
plt.savefig('patient_graph.png')  # Simpan grafik sebagai file gambar
plt.show()
