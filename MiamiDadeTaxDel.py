# This file was writen by Carick Brandt in 5/2023
# Import the needed modules
import os
import pandas as pd

# Check if the end of a string is " LE" with nothing after it
def CheckLE(Name: str):
    try:
        if Name.endswith(" LE"):
            return Name[:-3]
        elif Name.endswith(" (LE)"):
            return Name[:-5]
    except:
        print("Error in CheckLE. Just Returning the Name: " + Name)
        return Name
    return Name


# Check if the Name has a " &". If it is we want what comes before " &".
def CheckAnd(Name: str):
    if isinstance(Name, str) and " &" in Name:
        if len(Name.split(" &")[0].split(" ")) > 1:
            return Name.split(" &")[0]
        else:
            return Name.split(" ")[0] + " " + Name.split(" ")[-1]
    else:
        return Name


# Check for Common Suffices For a persons Name and remove them from the name
def CheckSuffices(Name: str):
    Suffices = [" JR", " SR", " II", " III", " IV"]
    Name = CheckLE(Name)
    Name = CheckAnd(Name)
    for Suffix in Suffices:
        if Name.endswith(Suffix):
            return Name.replace(Suffix, "")
    return Name


def CheckCompany(Name: str):
    SplitInfo = ["EST OF", " LLC", " (EST OF)", " (TR)", " TR", " TRS", " LP", " INC", " JTRS", " TRUST", " LIV",
                 " ARENAS",
                 " INVESTMENTS", "SETTLES", "INTERNATIONAL", "INVESTMENT", "MIAMI-DADE", "CITY", "COUNTY", "LTD",
                 "CORP",
                 "FUND", "PARTNERSHIP", "PARTNERS", "PARTNER", "ASSOCIATES", "ASSOCIATE", "ASSOC", "DEVELOPMENT",
                 "HABITAT", " EST", "MISSIONARY", "CHURCH", "RESIDENTIAL", "NEW LIFE", "OUTREACH",
                 "COMMUNITY", "BEACH", "TEMPLE", "GOD", "MINISTRIES", "RANCHES", "POST", "TOWNHOMES", "HOUSING",
                 "METHODIST", "CONSULTANCY", "PROJECT", "ESTATE", "INVESTORS", "CENTER", "CLUB",
                 "ENTERPRISE", "ORTHODOX", "TABERNACLE", "HOSPITAL", "ARCHBISHOP", "STREET", "CONFERENCE ASSN",
                 "REALITY",
                 "ARCHDIOCESE", "DIOCESE", "(AGD)", "TRUST", ]
    Name = CheckAnd(Name)
    for Split in SplitInfo:
        if Split in Name:
            return True
    return False


# Check if the name is multiple names back to back. if so we only care about the first set of names
def CheckMultipleNames(Name: str):
    LastNames = ["De la Cruz", "De la Fuente", "De la Garza", "De la Paz", "De la Rosa", "De la Torre", "De los Reyes",
                 "De los Santos", "Sureda", "Alvarez", "Castillo", "Cruz", "Delgado", "Fernandez", "Garcia", "Gonzalez",
                 "Hernandez", "Lopez", "Martinez", "Moreno", "Perez", "Ramirez", "Rivera", "Rodriguez", "Sanchez",
                 "Torres", "Vega", "Acosta", "Acevedo", "Aguilar", "Alonso", "Alvarado", "Amador", "Amaya", "Andrade",
                 "Araujo", "Arias", "Arroyo", "Avila", "Baez", "Baltazar", "Barajas", "Barrientos", "Batista",
                 "Becerra", "Beltran", "Benitez", "Bermudez", "Blanco", "Bonilla", "Borges", "Bravo", "Brito", "Burgos",
                 "Caballero", "Cabrera", "Cadena", "Caldera", "Camacho", "Camarillo", "Campos", "Canales", "Cantero",
                 "Caraballo", "Cardenas", "Carmona", "Carranza", "Carrasco", "Carrera", "Carrero", "Carrion", "Casas",
                 "Castaneda", "Castillo", "Castro", "Cavazos", "Caparros", "Cepeda", "Cervantes", "Chacon", "Chapa",
                 "Chavez", "Cisneros", "Collazo", "Colon", "Contreras", "Cordero", "Cordova", "Cornejo", "Cortes",
                 "Cotto", "Covarrubias", "Cuevas", "Davila", "De Jesus", "Del Rio", "Delgado", "Diaz", "Diez", "Duarte",
                 "Dueñas", "Duran", "Enriquez", "Escalante", "Escamilla", "Escobar", "Escobedo", "Espinal", "Espino",
                 "Espinoza", "Estrella", "Fajardo", "Farias", "Feliciano", "Felix", "Figueroa", "Flores", "Franco",
                 "Fuentes", "Galindo", "Gallardo", "Gallegos", "Galvan", "Gamboa", "Garcilazo", "Garibay", "Garza",
                 "Gastelum", "Gil", "Giron", "Gomez", "Gonzales", "Gracia", "Granados", "Guajardo", "Guardado",
                 "Guerra", "Guerrero", "Guevara", "Gutierrez", "Haro", "Henriquez", "Herrera", "Hidalgo", "Huerta",
                 "Ibarra", "Iniguez", "Jaime", "Jimenez", "Juarez", "Jurado", "Lara", "Leal", "Leiva", "Leon", "Leyva",
                 "Lima", "Lira", "Llamas", "Loera", "Longoria", "Lopez", "Lozano", "Lucas", "Luevano", "Lugo", "Luna",
                 "Macias", "Madrid", "Maldonado", "Mancilla", "Manriquez", "Manzo", "Marin", "Marquez", "Martinez",
                 "Mascorro", "Maya", "Mayorga", "Medina", "Mejia", "Melendez", "Mena", "Mendez", "Mendoza", "Mercado",
                 "Meza", "Miramontes", "Mireles", "Miranda", "Mojica", "Molina", "Montalvo", "Montañez", "Montenegro",
                 "Montero", "Montes", "Montez", "Montoya", "Mora", "Morales", "Moreno", "Mosqueda", "Moya", "Munguia",
                 "Murillo", "Najera", "Naranjo", "Nava", "Navarrete", "Navarro", "Nazario", "Nevarez", "Niño",
                 "Noriega", "Nuñez", "Ocampo", "Ochoa", "Ojeda", "Oliva", "Olivares", "Olivera", "Olivo", "Olivares",
                 "Olvera", "Ontiveros", "Oquendo", "Ordaz", "Orellana", "Ornelas", "Orosco", "Orozco", "Ortega",
                 "Ortiz", "Osorio", "Pacheco", "Padilla", "Palacios", "Pantoja", "Parada", "Parra", "Paz", "Pedraza",
                 "Pelayo", "Pena", "Peña", "Penaloza", "Perales", "Peralta", "Perea", "Pereira", "Pereyra", "Perla",
                 "Pineda", "Pizarro", "Plascencia", "Polanco", "Portillo", "Posada", "Preciado", "Prieto", "Puga",
                 "Quezada", "Quintana", "Quintanilla", "Quintero", "Quiroz", "Ramos", "Rangel", "Raya", "Real", "Reyes",
                 "Reyna", "Reynoso", "Rico", "Rincon", "Rios", "Rivas", "Rivero", "Robledo", "Robles", "Rocha",
                 "Rodarte", "Rojo", "Roldan", "Rolón", "Román", "Romero", "Rosado", "Rosales", "Rosario", "Rosas",
                 "Roybal", "Rubio", "Ruelas", "Ruiz", "Saavedra", "Salas", "Salazar", "Salcedo", "Salcido", "Saldivar",
                 "Salgado", "Salinas", "Samaniego", "Sanabria", "Sanches", "Sandoval", "Santacruz", "Santana",
                 "Santiago", "Santillan", "Santos", "Sauceda", "Saucedo", "Segovia", "Sepulveda", "Serna", "Serrano",
                 "Sevilla", "Sierra", "Silva", "Solano", "Solis", "Soliz", "Solorio", "Soria", "Sosa", "Sotelo", "Soto",
                 "Suarez", "Tafolla", "Tamez", "Tamayo", "Tavarez", "Tejada", "Tejeda", "Terrazas", "Terriquez",
                 "Tijerina", "Tirado", "Toledo", "Tomas", "Toro", "Torres", "Trejo", "Trevino", "Trujillo", "Urbina",
                 "Uribe", "Valadez", "Valdes", "Valdez", "Valdivia", "Valencia", "Valentin", "Valenzuela", "Valladares",
                 "Valle", "Vallejo", "Valles", "Vargas", "Vasquez", "Vega", "Velasco", "Velazquez", "Velez", "Venegas",
                 "Vera", "Verdugo", "Vergara", "Viera", "Vigil", "Villa", "Villagomez", "Villalobos", "Villanueva",
                 "Villarreal", "Villegas", "Yañez", "Ybarra", "Zambrano", "Zamora", "Zapata", "Zaragoza", "Zavala",
                 "Zelaya", "Zepeda", "Zuniga", "Matos", "Cuadrado", "Arrufat", "Boyd", "Brandt", "Morera", "Tacuri",
                 "Monteagudo", "Toruno", "Consuegra", "Carrasco", "Carrillo", "Carrion", "Cortes", "Cruz", "Davila",
                 "Diaz", "Dominguez", "Duarte", "Echeverria", "Escobar", "Escobedo", "Espinoza", "Estrella", "Fajardo",
                 "Farias", "Feliciano", "Fernandez", "Ferrer", "Fierro", "Flores", "Fonseca", "Franco", "Fuentes",
                 "Galindo", "Gallego", "Galvez", "Garcia", "Garza", "Gomez", "Gonzales", "Gonzalez", "Gracia",
                 "Guajardo", "Guerra", "Guerrero", "Guevara", "Gutierrez", "Guzman", "Hernandez", "Herrera", "Hidalgo",
                 "Hinojosa", "Ibarra", "Iglesias", "Jaime", "Jaimes", "Jaramillo", "Jimenez", "Juarez", "Jurado",
                 "Lara", "Leal", "Leiva", "Leon", "Leyva", "Linares", "Lira", "Llamas", "Lobato", "Lomeli", "Longoria",
                 "Lopez", "Lorenzo", "Lozano", "Lucero", "Lucio", "Luevano", "Lugo", "Luna", "Macias", "Madera",
                 "Madrid", "Madrigal", "Maestas", "Maldonado", "Manriquez", "Marin", "Marquez", "Martinez", "Medina",
                 "Puerto", "Palma", "Mohamed", "Lopez", "Junco", "Diaz", "Lopez", "ROJAS", "BAEZ", "Chow", "Fernandez",
                 "Parras", "Grullon", "MILAGROS", "Milfort", "Del Carmen", "Hernandez", "Navas", "Escudero", "Poessy",
                 "Sanchez", "Suarez", "Roche", "Morales", "Chacon", "Montes"
                 ]
    Name = Name.title()
    LastNames = [LastName.title() for LastName in LastNames]
    FullName = Name
    Name = Name.split(" ")
    for name in Name:
        for LastName in LastNames:
            try:
                if LastName in name:
                    index = Name.index(name)
                    FirstName = FullName.split(" ")[0]
                    LastName = FullName.split(" ")[index]
                    MiddleName = " ".join(FullName.split(" ")[1:index])
                    return FirstName, MiddleName, LastName
            except:
                pass
    return Name[0], "", Name[-1]


# This function will the dataframe into two dataframes, one for the Companies or Esstates and one for the individuals.
# For the Individuals it will also split the names into firstName, MiddleName, LastName.
# Filepath is the path to the file that needs to be split.
# ColumnName is the name of the Column that has the names that need to be split.
def SplitNames(Filepath: str, ColumnName: str):
    df = pd.read_csv(Filepath)
    df.rename(columns={ColumnName: "First Name"}, inplace=True)
    df.insert(df.columns.get_loc("First Name") + 1, "Last Name", "")
    df.insert(df.columns.get_loc("First Name") + 1, "Middle Name", "")
    df.dropna(subset=["First Name"], inplace=True)
    Individuals = pd.DataFrame(columns=df.columns)
    Companies = pd.DataFrame(columns=df.columns)
    for index, row in df.iterrows():
        if CheckCompany(row["First Name"]):
            Companies.loc[index] = row
        else:
            Individuals.loc[index] = row
            Name = CheckSuffices(row["First Name"])
            if ColumnName == "Name":
                try:
                    first, middle, last = CheckMultipleNames(Name)
                    Individuals.loc[index, "First Name"] = first
                    if middle != "":
                        Individuals.loc[index, "Middle Name"] = middle
                    Individuals.loc[index, "Last Name"] = last
                except:
                    Individuals.loc[index, "First Name"] = Name.split(" ")[0]
                    Individuals.loc[index, "Last Name"] = Name.split(" ")[-1]
                    continue
            if len(Name.split(" ")) == 2:
                Individuals.loc[index, "First Name"] = Name.split(" ")[0]
                Individuals.loc[index, "Last Name"] = Name.split(" ")[1]
            elif len(Name.split(" ")) == 3:
                Individuals.loc[index, "First Name"] = Name.split(" ")[0]
                Individuals.loc[index, "Middle Name"] = Name.split(" ")[1]
                Individuals.loc[index, "Last Name"] = Name.split(" ")[2]
            elif len(Name.split(" ")) > 3:
                Individuals.loc[index, "First Name"] = Name.split(" ")[0]
                Individuals.loc[index, "Middle Name"] = Name.split(" ")[1] + " " + Name.split(" ")[2]
                Individuals.loc[index, "Last Name"] = Name.split(" ")[3]
    Individuals.reset_index(drop=True, inplace=True)
    Companies.reset_index(drop=True, inplace=True)
    new_df = pd.concat([Individuals, Companies], ignore_index=True)
    return new_df


# Main call
if __name__ == "__main__":
    file = os.getcwd() + "\\MiamiDadeCV60Days.csv"
    People, Trust = SplitNames(file, ColumnName='Name')
    PeopleSave = os.getcwd() + "\\MiamiDadeCVIndividuals1.csv"
    People.to_csv(PeopleSave, index=False)
    TrustSave = os.getcwd() + "\\MiamiDadeCVTrusts1.csv"
    Trust.to_csv(TrustSave, index=False)
    print("Completed!")
