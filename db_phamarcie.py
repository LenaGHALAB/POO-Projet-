import sqlite3
db=sqlite3.connect("pharmacie.db")

def create_table():
    conn = sqlite3.connect("pharmacie.db")
    cur = conn.cursor()

    #Table des médicaments
    cur.execute("""
    CREATE TABLE IF NOT EXISTS medicaments (
        id INTEGER PRIMARY KEY,
        nom TEXT NOT NULL,
        code_barre TEXT UNIQUE,
        description TEXT,
        quantite INTEGER NOT NULL DEFAULT 0 CHECK(quantite >= 0),
        prix REAL NOT NULL CHECK(prix >= 0),
        date_expiration DATE,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        mise_a_jour TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    #Table des clients
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        prenom TEXT NOT NULL,
        naissance DATE NOT NULL,
        phone TEXT,
        num_assurance TEXT,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        mise_a_jour TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    #Table des ventes
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vente(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_medicament INTEGER NOT NULL,
    id_client INTEGER,
    quantite INTEGER NOT NULL CHECK(quantite > 0),
    prix_unitaire REAL NOT NULL CHECK(prix_unitaire > 0),
    prix_total REAL NOT NULL CHECK(prix_total > 0),
    date_vente TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    pharmacien TEXT,
    FOREIGN KEY (id_medicament) REFERENCES medicaments(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (id_client) REFERENCES clients(id) ON DELETE SET NULL ON UPDATE CASCADE
    ); 
    """)

    #cette partie concerne la mise a jour
    cur.execute("""
       CREATE TRIGGER IF NOT EXISTS trg_medicaments_updated_at
       AFTER UPDATE ON medicaments
       FOR EACH ROW
       BEGIN
           UPDATE medicaments SET mise_a_jour = CURRENT_TIMESTAMP WHERE id = OLD.id;
       END;
       """)
    cur.execute("""
       CREATE TRIGGER IF NOT EXISTS trg_clients_updated_at
       AFTER UPDATE ON clients
       FOR EACH ROW
       BEGIN
           UPDATE clients SET mise_a_jour = CURRENT_TIMESTAMP WHERE id = OLD.id;
       END;
       """)

    conn.commit()

def remplir(conn: sqlite3.Connection):
    cur = conn.cursor()

    # le pharmacien peut ajouter des codes
    n = int(input("Combien de médicaments voulez-vous ajouter ? "))
    for i in range(n):
        nom = input("Nom du médicament : ").strip()
        description = input("Description : ").strip()
        code_barre = input("Code-barres : ").strip()
        prix = float(input("Prix unitaire : "))
        quantite = int(input("Quantité : "))
        date_expiration = input("Date d'expiration (YYYY-MM-DD) : ").strip()

        try:
            cur.execute("""
                INSERT INTO medicaments (nom, description, code_barre, prix, quantite, date_expiration)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nom, description, code_barre, prix, quantite, date_expiration))
        except sqlite3.IntegrityError as e:
            print(f"Erreur : {e}. Médicament non ajouté.")

    # Ajouter des clients via l'utilisateur
    n_clients = int(input("Combien de clients voulez-vous ajouter ? "))
    for i in range(n_clients):
        nom = input("Nom : ").strip()
        prenom = input("Prénom : ").strip()
        naissance = input("Date de naissance (YYYY-MM-DD) : ").strip()
        phone = input("Téléphone : ").strip()
        num_assurance = input("Numéro d'assurance : ").strip()

        try:
            cur.execute("""
                INSERT INTO clients (nom, prenom, naissance, phone, num_assurance)
                VALUES (?, ?, ?, ?, ?)
            """, (nom, prenom, naissance, phone, num_assurance))
        except sqlite3.IntegrityError as e:
            print(f"Erreur : {e}. Client non ajouté.")

    conn.commit()
    print("Données ajoutées avec succès !")

create_table()
#remplir(db)