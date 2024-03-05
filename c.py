import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

RANDOM_SEED = 42
NUM_PROCESOS = [25, 50, 100, 150, 200]
INTERVALOS = [10, 5, 1]
CPU_SPEED = 3
MEMORIA_RAM = 100

tiempos_promedio = []
desviaciones_std = []

class SistemaOperativo:
    def __init__(self, env, num_procesos, intervalo):
        self.env = env
        self.procesador = simpy.Resource(env, capacity=1)
        self.ram = simpy.Container(env, init=MEMORIA_RAM, capacity=MEMORIA_RAM)
        self.intervalo = intervalo
        self.num_procesos = num_procesos
        self.tiempos_ejecucion = []

    def llegada_proceso(self):
        for i in range(self.num_procesos):
            p = Proceso(i, self.env, self.procesador, self.ram, self.tiempos_ejecucion)
            self.env.process(p.proceso())
            yield self.env.timeout(random.expovariate(1.0 / self.intervalo))

class Proceso:
    def __init__(self, id, env, procesador, ram, tiempos_ejecucion):
        self.id = id
        self.env = env
        self.procesador = procesador
        self.ram = ram
        self.tiempos_ejecucion = tiempos_ejecucion
        self.memoria_necesaria = random.randint(1, 10)
        self.instrucciones_totales = random.randint(1, 10)
        self.instrucciones_restantes = self.instrucciones_totales

    def proceso(self):
        memoria_obtenida = yield self.ram.get(self.memoria_necesaria)
        # if memoria_obtenida is None:
        #    return  # Salir del proceso si no se obtiene la memoria
        inicio_proceso = self.env.now

        while self.instrucciones_restantes > 0:
            print("Proceso iniciado.")
            with self.procesador.request() as req:
                yield req

                # Simulación de ejecución del proceso en el CPU
                instrucciones_ejecutadas = min(CPU_SPEED, self.instrucciones_restantes)
                yield self.env.timeout(1)  # 1 unidad de tiempo
                self.instrucciones_restantes -= instrucciones_ejecutadas

                if self.instrucciones_restantes <= 0:
                    tiempo_total = self.env.now - inicio_proceso
                    print("Proceso terminado.")
                    self.tiempos_ejecucion.append(tiempo_total)
                    self.ram.put(self.memoria_necesaria)  # Devolver la memoria al contenedor de RAM
                    break

                # Simulación de operaciones de I/O
                if random.randint(1, 21) == 1:
                    yield self.env.timeout(random.randint(1, 21))

def simular(num_procesos, intervalo):
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    sistema = SistemaOperativo(env, num_procesos, intervalo)
    env.process(sistema.llegada_proceso())
    env.run()

    tiempo_promedio = np.mean(sistema.tiempos_ejecucion)
    desviacion_std = np.std(sistema.tiempos_ejecucion)
    return tiempo_promedio, desviacion_std

resultados = []

for num_proceso in NUM_PROCESOS:
    for intervalo in INTERVALOS:
        tiempo_promedio, desviacion_std = simular(num_proceso, intervalo)
        resultados.append((num_proceso, intervalo, tiempo_promedio, desviacion_std))

for resultado in resultados:
    print(f"Número de procesos: {resultado[0]}, Intervalo: {resultado[1]}, Tiempo promedio: {resultado[2]}, Desviación estándar: {resultado[3]}")


