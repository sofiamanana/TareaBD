import pyodbc
import csv
from random import *

#Conexion:

conn = pyodbc.connect("DRIVER={Oracle en OraDB18Home1}; DBQ=XE;Uid=sofita;Pwd=sofia")

'''
Nombre de funcion: prKeyPoyo
Descripcion: altera la tabla para agregar la primary key a la tabla POYO.
Input: conn -> conexion a la base de datos.
Outputs: no genera ningun output
'''
def prKeyPoyo(conn):
    cur = conn.cursor()
    cur.execute("""
                    ALTER TABLE POYO
                    ADD CONSTRAINT name_pkP PRIMARY KEY (NAME);
                    """)
    cur.commit()

'''
Nombre de funcion: crearPoyo.
Descripcion: crea la tabla POYO, ajustando cada uno de los atributos.
Input: conn -> conexion a la base de datos.
Outputs: no genera ningun output
'''

def crearPoyo(conn):
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE POYO(
            ID_P INTEGER NOT NULL,
            NAME VARCHAR2(50) NOT NULL,
            TIPO_1 VARCHAR(25) NOT NULL,
            TIPO_2 VARCHAR(25),
            HP_MAX INTEGER NOT NULL,
            LEGENDARIO INTEGER NOT NULL)    
        """
        )
    cur.commit()
    prKeyPoyo(conn)

'''
Nombre de funcion: prKeySansanito.
Descripcion: altera la tabla para agregar la primary key a la tabla Sansanito.
Input: conn -> conexion a la base de datos.
Outputs: no genera ningun output
'''

def prKeySansanito(conn):
    cur = conn.cursor()
    cur.execute("""
                    ALTER TABLE Sansanito
                    ADD CONSTRAINT name_pkS PRIMARY KEY (id);
                    """)
    cur.commit()

'''
Nombre de funcion: crearSansanito.
Descripcion: crea la tabla Sansanito, ajustando cada uno de los atributos.
Input: conn -> conexion a la base de datos.
Outputs: no genera ningun output.
'''

def crearSansanito(conn):
    cur = conn.cursor()
    cur.execute(
            """CREATE TABLE Sansanito (
                id NUMBER GENERATED BY DEFAULT ON NULL AS IDENTITY,
                ID_P INTEGER NOT NULL,
                NAME VARCHAR2(50) NOT NULL,
                TIPO_1 VARCHAR(25) NOT NULL,
                TIPO_2 VARCHAR(25),
                HP_ACTUAL INTEGER NOT NULL,
                LEGENDARIO INTEGER NOT NULL,
                HP_MAX INTEGER NOT NULL,
                ESTADO VARCHAR(50),
                FECHA_HORA TIMESTAMP,
                PRIORIDAD INTEGER
            );"""
        )
    cur.commit()
    prKeySansanito(conn)    

'''
Nombre de funcion: borrarPoyo.
Descripcion: borra la tabla POYO.
Input: conn -> conexion a la base de datos.
Outputs: no genera ningun output.
'''

def borrarPoyo(conn):
    cur = conn.cursor()
    cur.execute("DROP TABLE POYO")
    cur.commit()

'''
Nombre de funcion: borrarSansanito.
Descripcion: borra la tabla Sansanito.
Input: conn -> conexion a la base de datos.
Outputs: no genera ningun output.
'''

def borrarSansanito(conn):
    cur = conn.cursor()
    cur.execute("DROP TABLE Sansanito")
    cur.commit()

'''
Nombre de funcion: trans_legendario.
Descripcion: transforma el string True o False del csv a 1 o 0, dependiendo del caso.
Input: conn -> conexion a la base de datos.
Outputs: retorna 0 si recibe False y 1 si recibe True.
'''

def trans_legendario(i):
    if i == 'True':
        return 1
    else:
        return 0

'''
Nombre de funcion: rellenarPoyo.
Descripcion: rellena con datos la tabla Poyo, los datos son obtenidos del csv pokemon.
Input: conn -> conexion a la base de datos.
Outputs: no genera ningun output.
'''

def rellenarPoyo(conn):
    cur = conn.cursor()
    l_cont = 0
    with open('pokemon.csv') as file:
        reader = csv.reader(file, delimiter=',')
        for linea in reader:
            if l_cont == 0:
                l_cont+=1
            else:
                id_pokedex = int(linea[0])
                nombre = str(linea[1])
                tipo1 = str(linea[2])
                tipo2 = str(linea[3])
                hp_max = int(linea[5])
                legend = linea[12]
                legendario = trans_legendario(legend)

                cur.execute(
                    f"""
                        INSERT INTO POYO (ID_P,NAME,TIPO_1,TIPO_2,HP_MAX,LEGENDARIO)
                        VALUES ('{id_pokedex}','{nombre}','{tipo1}','{tipo2}','{hp_max}','{legendario}')
                    """
                    )
                cur.commit()

'''
Nombre de funcion: trigger.
Descripcion: crea un trigger donde se actualice la prioridad cada vez que un pokemon sea modificado.
Input: conn -> conexion a la base de datos.
Outputs: no genera ningun output.
'''

def trigger(conn):
    cur = conn.cursor()
    cur.execute("""CREATE OR REPLACE TRIGGER prioridad
                    BEFORE UPDATE OF HP_ACTUAL,ESTADO ON Sansanito FOR EACH ROW
                    BEGIN
                        IF UPDATING THEN
                            IF :NEW.ESTADO = 'Null' THEN
                                :new.PRIORIDAD := :new.HP_MAX - :new.HP_ACTUAL;
                            ELSE
                                :NEW.PRIORIDAD := :new.HP_MAX - :NEW.HP_ACTUAL + 10;
                            END IF;
                        END IF;
                    END;""")
    cur.commit()

'''
Nombre de funcion: rellenarSansanito.
Descripcion: rellena con datos la tabla Sansanito, los datos son obtenidos al azar de la tabla Poyo. Llama a la funcion trigger para adjuntarlo a la tabla.
Input: conn -> conexion a la base de datos.
Outputs: no genera ningun output.
'''

def rellenarSansanito(conn):
    cur = conn.cursor()
    estados = ['Null','Envenenado', 'Paralizado', 'Quemado', 'Dormido', 'Congelado']
    capacidad=0
    while capacidad<50:
        cur.execute("SELECT * FROM POYO SAMPLE(1)")
        pokemon = cur.fetchone()
        id_pokedex, nombre, tipo1, tipo2, hp_max, legendario = pokemon
        nom='a'

        if legendario == 1:
            cur.execute("SELECT * FROM Sansanito WHERE NAME = ?;",nombre)
            nom = cur.fetchone()       

        hp_actual = randint(0,hp_max)
        prioridad = hp_max-hp_actual
        est = randint(0,5)
        estado = estados[est]
        if estado != 'Null':
            prioridad+=10

        if nom!=nombre:
            if legendario == 1:
                capacidad+=5
            else:
                capacidad+=1
            cur.execute(
                f"""
                    INSERT INTO Sansanito (ID_P,NAME,TIPO_1,TIPO_2,HP_ACTUAL,LEGENDARIO,HP_MAX,ESTADO,FECHA_HORA,PRIORIDAD)
                    VALUES ('{id_pokedex}','{nombre}','{tipo1}','{tipo2}','{hp_actual}','{legendario}','{hp_max}','{estado}',LOCALTIMESTAMP,'{prioridad}');
                """)
            cur.commit()
    trigger(conn)

'''
Nombre de funcion: read.
Descripcion: lee los datos de la tabla Sansanito y a pedido del usuario, los imprime a pantalla.
Input: conn -> conexion a la base de datos.
Outputs: no genera ningun output.
'''

def read(conn):
    cur = conn.cursor()
    inp = ' '

    cur.execute("SELECT count(ID) FROM Sansanito;")
    max_size = int(cur.fetchone()[0])

    while inp != '*':
        print('-------------------------------------------------------')
        print("""\n Ingrese los numeros de id a ver, separados por coma: 
            * Para salir""")
        inp = input()
        if ',' in inp:
            inp = inp.strip().split(',')
            i = 0
            l = []
            try:

                for j in inp:
                    inp[i] = int(j)
                    i+=1
                
                for i in inp:
                    cur.execute("""SELECT * FROM Sansanito WHERE id = ?;""",(i))            
                    a = cur.fetchone()
                    l.append(a)                
                
                printLista(l, [])

            except:
                print("Input invalido")

        elif inp[0] in '0123456789':
            try:
                inp = int(inp)
                if inp>max_size:
                    print("Indice fuera de rango")
                else:
                    cur.execute("SELECT * FROM Sansanito WHERE id = ?;",(inp))
                    a = cur.fetchone()
                    printLista(a, [])

            except:
                print("Input invalido")
        
        elif inp == '*':
            continue
        else:
            print("Input Invalido")

'''
Nombre de funcion: update.
Descripcion: actualiza los datos de la tabla Sansanito. Los nuevos datos son pedidos por pantalla y solo se puede actualizar el Hp Actual y el Estado.
Input: conn -> conexion a la base de datos.
Outputs: no genera ningun output.
'''

def update(conn):
    cur = conn.cursor()
    inp = ' '
    estados = ['Null','Envenenado', 'Paralizado', 'Quemado', 'Dormido', 'Congelado']

    cur.execute("SELECT id FROM Sansanito ORDER BY id DESC")
    max_size = int(cur.fetchone()[0])

    while inp != '*':

        print('-------------------------------------------------------')
        print("""\n Ingrese el id a actualizar: 
            * Para salir""")
        inp = input()

        if inp[0] in '0123456789':
            try: 
                inp = int(inp)
                if inp > max_size:
                    print("Indice fuera de rango")
                else:
                    print('''¿Que desea actualizar
            (1) Hp Actual
            (2) Estado''')
                    opcion = input()

                    try:
                        opcion = int(opcion)
                        if opcion == 1:
                            print('Nuevo Hp Actual: ')
                            Nhp_actual = input()
                            try:
                                Nhp_actual = int(Nhp_actual)
                                cur.execute("SELECT * FROM Sansanito WHERE id = ?;",(inp))
                                pokemon = cur.fetchone()
                                hp_max = pokemon[7]
                                print(hp_max)

                                if Nhp_actual <= hp_max:
                                    cur.execute("""UPDATE Sansanito
                                                    SET HP_ACTUAL = ?
                                                    WHERE id = ?;""",(Nhp_actual,inp))
                                    cur.commit()
                                    print('Done')

                                else:
                                    print('No puede exceder el Hp Maximo de un pokemon')

                            except:
                                print('Hp invalido')
                        elif opcion == 2:
                            print('Nuevo estado: ')
                            est = input()

                            if est in estados:
                                cur.execute("""UPDATE Sansanito
                                                SET ESTADO = ?
                                                WHERE id = ?;""",(est,inp))
                                cur.commit()
                                print('Done')
                        else:
                            print('Input invalido')
                    except:
                        print('Input invalido')
            except:
                print('Input invalido')

'''
Nombre de funcion: delete.
Descripcion: borra a un pokemon de la tabla a pedido del usuario. El id a borrar es pedido por pantalla.
Input: conn -> conexion a la base de datos.
Outputs: no genera ningun output.
'''

def delete(conn):  
    cur = conn.cursor()
    inp = ' '

    while inp != '*':
        print('-------------------------------------------------------')
        print("""\n Ingrese el id a borrar: 
            * Para salir""")
        inp = input()

        if inp[0] in '0123456789':
            inp = int(inp)

            cur.execute("DELETE FROM Sansanito WHERE id = ?;",(inp))
            cur.commit()
            print('Pokemon borrado')

'''
Nombre de funcion: calc_capacidad.
Descripcion: calcula la capacidad de Sansanito.
Input: conn -> conexion a la base de datos.
Outputs: retorna la capacidad de la tabla.
'''

def calc_capacidad(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM Sansanito;")
    a = cur.fetchall()
    capacidad = 0
    for i in a:
        if i[6] == 0:
            capacidad +=1
        elif i[6] == 1:
            capacidad+=5
    return capacidad

'''
Nombre de funcion: create.
Descripcion: agrega un pokemon a la tabla, cuidando de no sobrepasar la capacidad.
Input: conn -> conexion a la base de datos.
Outputs: no genera ningun output.
'''

def create(conn):
    cur = conn.cursor()
    inp = ' '
    while inp != '*':
        print('-------------------------------------------------------')
        print("""\n Ingrese el Nombre del pokedex a ingresar: 
            * Para salir""")
        inp = input()
        if inp != '*':
            cur.execute("SELECT * FROM POYO WHERE NAME = ?;",(inp))
            pokemon = cur.fetchone()
            id_pokedex, nombre, tipo_1, tipo_2, hp_max, legendario = pokemon

            print("Ingrese Hp Actual: ")
            hp_actual = input()
            hp_actual = int(hp_actual)
            if hp_actual < hp_max:
                
                print("Ingrese estado del pokemon: ")
                print("""-Envenenado
                        -Paralizado
                        -Quemado
                        -Dormido
                        -Congelado
                        -Null """)
                estado = input()

                if estado != 'Null':
                    prioridad = hp_max - hp_actual
                else:
                    prioridad = hp_max - hp_actual + 10
                
                capacidad = calc_capacidad(conn)
                if capacidad == 50:
                    cur.execute("SELECT * FROM Sansanito WHERE LEGENDARIO = ? ORDER BY PRIORIDAD ASC;",(legendario))
                    poke = cur.fetchone()

                    priori = poke[10]
                    if priori < prioridad:
                        if legendario == 1:
                            if poke[2]!=nombre:
                                cur.execute("DELETE FROM Sansanito WHERE ID = ?;",(poke[0]))
                                cur.execute(
                                            f"""
                                                INSERT INTO Sansanito (ID_P,NAME,TIPO_1,TIPO_2,HP_ACTUAL,LEGENDARIO,HP_MAX,ESTADO,FECHA_HORA,PRIORIDAD)
                                                VALUES ('{id_pokedex}','{nombre}','{tipo_1}','{tipo_2}','{hp_actual}','{legendario}','{hp_max}','{estado}',LOCALTIMESTAMP,'{prioridad}');
                                            """)
                                print('Pokemon ingresado') 
                            else:
                                print('No se ingreso el pokemon')
                        else:
                            cur.execute("DELETE FROM Sansanito WHERE ID = ?;",(poke[0]))
                            cur.execute(
                                        f"""
                                            INSERT INTO Sansanito (ID_P,NAME,TIPO_1,TIPO_2,HP_ACTUAL,LEGENDARIO,HP_MAX,ESTADO,FECHA_HORA,PRIORIDAD)
                                            VALUES ('{id_pokedex}','{nombre}','{tipo_1}','{tipo_2}','{hp_actual}','{legendario}','{hp_max}','{estado}',LOCALTIMESTAMP,'{prioridad}');
                                        """)
                            print('Pokemon ingresado') 

                    else:
                        print('No se ingreso el pokemon')
                else:
                    if capacidad <=45 and legendario == 1:
                        cur.execute(
                                    f"""
                                        INSERT INTO Sansanito (ID_P,NAME,TIPO_1,TIPO_2,HP_ACTUAL,LEGENDARIO,HP_MAX,ESTADO,FECHA_HORA,PRIORIDAD)
                                        VALUES ('{id_pokedex}','{nombre}','{tipo_1}','{tipo_2}','{hp_actual}','{legendario}','{hp_max}','{estado}',LOCALTIMESTAMP,'{prioridad}');
                                    """)     
                        print('Pokemon ingresado') 
                    elif capacidad <= 49 and legendario == 0:
                        cur.execute(
                                    f"""
                                        INSERT INTO Sansanito (ID_P,NAME,TIPO_1,TIPO_2,HP_ACTUAL,LEGENDARIO,HP_MAX,ESTADO,FECHA_HORA,PRIORIDAD)
                                        VALUES ('{id_pokedex}','{nombre}','{tipo_1}','{tipo_2}','{hp_actual}','{legendario}','{hp_max}','{estado}',LOCALTIMESTAMP,'{prioridad}');
                                    """) 
                        print('Pokemon ingresado') 
        cur.commit()       

'''
Nombre de funcion: mayor_prioridad.
Descripcion: genera una view con los 10 pokemones con mayor prioridad y luego los imprime por pantalla.
Input: conn -> conexion a la base de datos.
Outputs: no genera ningun output.
'''

def mayor_prioridad(conn):
    cur = conn.cursor()
    cur.execute("""CREATE OR REPLACE VIEW MAYOR_PRIORIDAD AS
                    SELECT * FROM (SELECT * FROM Sansanito ORDER BY PRIORIDAD DESC) WHERE ROWNUM<=10;""")
    cur.commit()
    
    cur.execute("SELECT * FROM MAYOR_PRIORIDAD;")
    lista = cur.fetchall()
    printLista(lista, [])

'''
Nombre de funcion: menor_prioridad.
Descripcion: genera una view con los 10 pokemones con menor prioridad y luego los imprime por pantalla.
Input: conn -> conexion a la base de datos.
Outputs: no genera ningun output.
'''

def menor_prioridad(conn):
    cur = conn.cursor()
    cur.execute("""CREATE OR REPLACE VIEW MENOR_PRIORIDAD AS
                    SELECT * FROM (SELECT * FROM Sansanito ORDER BY PRIORIDAD ASC) WHERE ROWNUM<=10;""")
    cur.commit()
    
    cur.execute("SELECT * FROM MENOR_PRIORIDAD;")
    lista = cur.fetchall()
    printLista(lista, [])

'''
Nombre de funcion: legendarios.
Descripcion: imprime por pantalla todos los pokemones legendarios en la tabla Sansanito.
Input: conn -> conexion a la base de datos.
Outputs: no genera ningun output.
'''

def legendarios(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM Sansanito WHERE LEGENDARIO = 1;")
    lista = cur.fetchall()
    if lista != []:
        printLista(lista, [])
    else:
        print("No hay pokemones legendarios")

'''
Nombre de funcion: pokemon_viejo.
Descripcion: imprime por pantalla al pokemon que lleva mas tiempo ingresado en la tabla Sansanito.
Input: conn -> conexion a la base de datos.
Outputs: no genera ningun output.
'''

def pokemon_viejo(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM Sansanito ORDER BY FECHA_HORA ASC;")
    pok_viejo = cur.fetchone()
    printLista(pok_viejo,[])

'''
Nombre de funcion: estados.
Descripcion: muestra por pantalla los pokemones ordenados por estado.
Input: conn -> conexion a la base de datos.
Outputs: no genera ningun output.
'''

def estados(conn):
    cur = conn.cursor()

    inp = ' '
    while inp != '*':
        print("""Ingrese estado:
        -Null
        -Envenenado
        -Paralizado
        -Quemado
        -Dormido
        -Congelado
        * Para salir""")
        inp = input()
        if inp != '*':
            cur.execute("SELECT * FROM Sansanito WHERE ESTADO = ?;",(inp))
            lista = cur.fetchall()
            printLista(lista,[])

'''
Nombre de funcion: mas_repetido.
Descripcion: muestra el pokemon mas repetido en la tabla Sansanito.
Input: conn -> conexion a la base de datos.
Outputs: no genera ningun output.
'''

def mas_repetido(conn):
    cur = conn.cursor()
    cur.execute("""SELECT NAME, COUNT(NAME) AS REP 
                    FROM Sansanito
                    GROUP BY NAME
                    ORDER BY REP DESC;""")
    mas_rep = cur.fetchone()[0]
    rep = cur.fetchone()[1]
    print("El pokemon mas repetido es: ",mas_rep)
    print("Cantidad de repeticiones: ",rep)

'''
Nombre de funcion: agregarEspacio4.
Descripcion: agrega espacios a la lista o tupla que recibe, asi cuando se imprima la tabla en pantalla, quede ordenada. Funcion para listas de largo 4.
Input: tupla -> tupla o lista a agregar espacios.
Outputs: lista con los valores ordenados.
'''

def agregarEspacio4(tupla):
    l = []
    i = 0
    while i < len(tupla):

        if isinstance(tupla[i],float):
            tupla[i] = str(int(tupla[i]))
        else:
            tupla[i] = str(tupla[i])

        tupla[i] = tupla[i] + ' '*(23-len(tupla[i]))
        l.append(tupla[i])
        i+=1
    return l
    
'''
Nombre de funcion: agregarEspacio.
Descripcion: agrega espacios a la lista o tupla que recibe, asi cuando se imprima la tabla en pantalla, quede ordenada. Funcion para listas de largo 11.
Input: tupla -> tupla o lista a agregar espacios.
Outputs: lista con los valores ordenados.
'''

def agregarEspacio(tupla):
    l = []
    i = 0
    
    while i < len(tupla):
        if isinstance(tupla[i],float):
            tupla[i] = str(int(tupla[i]))
        else:
            tupla[i] = str(tupla[i])
        
        if i == 0 or i == 10:
            tupla[i] = tupla[i] + ' '*(4-len(tupla[i]))
        elif i == 1 or i == 5 or i ==6 or i == 7:
            tupla[i] = tupla[i] + ' '*(12-len(tupla[i]))
        elif i == 6:
            tupla[i] = tupla[i] + ' '*(8-len(tupla[i]))
        elif i == 2 or i == 3 or i == 4 or i == 8:
            tupla[i] = tupla[i] + ' '*(20-len(tupla[i]))
        elif i == 9:
            tupla[i] = tupla[i] + ' '*(26-len(tupla[i]))
        
        l.append(tupla[i])
        i+=1
    return l

'''
Nombre de funcion: printLista.
Descripcion: imprime una tabla ordenada.
Input: lista -> lista de datos a imprimir en la tabla, nombres -> lista con los nombres de los identificadores de cada columna.
Outputs: no genera ningun output.
'''

def printLista(lista, nombres):
    l = [] 
    if nombres == []:   
        nom = ['ID ', ' Id Pokedex ',' Nombre ',' Tipo 1 ', ' Tipo 2 ',' Hp Actual ',' Legend ', ' Hp Max ', ' Estado ', ' Hora de Ingreso ', ' Prioridad ']
            
        nom = agregarEspacio(nom)
        if isinstance(lista[0],float) or isinstance(lista[0],str):   
            a = agregarEspacio(lista)
            l.append("|".join([x for x in a]))

        else:
            for tupla in lista:
                tupla = agregarEspacio(tupla)            
                l.append("|".join([x for x in tupla]))
    else:
        nombres = agregarEspacio4(nombres)

        if isinstance(lista[0],float) or isinstance(lista[0],str):   
            a = agregarEspacio4(lista)
            l.append("|".join([x for x in a]))

        else:
            for tupla in lista:
                tupla = agregarEspacio4(tupla)            
                l.append("|".join([x for x in tupla]))

    if len(nombres) == 0:
        l.insert(0, "|".join([x for x in nom]))
    else:         
        l.insert(0, "| ".join([x for x in nombres]))

    for i in l:
        print(i)  
                
'''
Nombre de funcion: insertPokemon.
Descripcion: inserta a un pokemon en la base de datos.
Input: conn -> conexion a la base de datos.
Outputs: no genera ningun output.
'''

def insertPokemon(conn):
    create(conn)

'''
Nombre de funcion: tabla.
Descripcion: imprime los atributos Nombre, Hp Actual, Hp Maximo y prioridad de los pokemones de la tabla Sansanito.
Input: conn -> conexion a la base de datos.
Outputs: no genera ningun output.
'''

def tabla(conn):
    cur = conn.cursor()
    cur.execute("SELECT NAME,HP_ACTUAL,HP_MAX,PRIORIDAD FROM Sansanito ORDER BY PRIORIDAD DESC")
    lista = cur.fetchall()
    nom = [' Nombre', ' HP Actual', ' HP Maximo', ' Prioridad']
    printLista(lista, nom)

'''
Nombre de funcion: main.
Descripcion: ejecuta el programa principal que llama a todas las otras funciones, dando al usuario la opcion de que hacer.
Input: conn -> conexion a la base de datos.
Outputs: no genera ningun output.
'''

def main(conn):
    print("¡Bienvenido al Sansanito Pokemon!")

    print("Creando POYO...")

    borrarPoyo(conn)
    crearPoyo(conn)
    rellenarPoyo(conn)

    print("Creando Sansanito...")

    borrarSansanito(conn)
    crearSansanito(conn)
    rellenarSansanito(conn)

    
    inp = ''
    while inp!='*':
        print("""Escoja una de las siguientes opciones:
    (1) Operaciones CRUD
    (2) Ingresar un Pokemon
    (3) Ver los 10 Pokemones con mayor prioridad
    (4) Ver los 10 Pokemones con menor prioridad
    (5) Ver a Pokemones por estado
    (6) Ver a Pokemones legendarios
    (7) Ver al Pokemon con mas tiempo ingresado
    (8) Ver a los Pokemones mas repetidos
    (9) Ver tabla de Pokemones ordenados por: Nombre, HP Actual, HP Maximo y Prioridad.
    (*) Para salir""")
        inp = input()
        if inp != '*':
            inp = int(inp)

            if inp == 1:
                print("""Seleccione una de las opciones:
                (1) Create
                (2) Read
                (3) Update
                (4) Delete""")

                opcion = input()
                opcion = int(opcion)

                if opcion == 1:
                    create(conn)
                elif opcion == 2:
                    read(conn)
                elif opcion == 3:
                    update(conn)
                else:
                    delete(conn)
            elif inp == 2:
                insertPokemon(conn)
            elif inp == 3:
                mayor_prioridad(conn)
            elif inp == 4:
                menor_prioridad(conn)
            elif inp == 5:
                estados(conn)
            elif inp == 6:
                legendarios(conn)
            elif inp == 7:
                pokemon_viejo(conn)
            elif inp == 8:
                mas_repetido(conn)
            elif inp == 9:
                tabla(conn)
            else:
                print('Input invalido')

#Programa principal:

main(conn)

#Cierra la conexion con la base de datos.

conn.close()


