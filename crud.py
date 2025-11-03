import sqlite3
from datetime import datetime

# --- Connexion à la base de données ---
def connect_db():
    conn = sqlite3.connect("pharmacie.db")
    conn.execute("PRAGMA foreign_keys = ON;")  # Activer les clés étrangères
    return conn

# --- GESTION DES MÉDICAMENTS ---

def ajouter_medicament(nom, code_barre, description, quantite, prix, date_expiration=None):

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO medicaments (nom, code_barre, description, quantite, prix, date_expiration)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nom, code_barre, description, quantite, prix, date_expiration))
        conn.commit()
        print(f"Médicament '{nom}' ajouté avec succès.")
        return True
    except sqlite3.IntegrityError:
        print(f"Erreur : Un médicament avec le code-barres '{code_barre}' existe déjà.")
        return False
    except Exception as e:
        print(f"Erreur lors de l'ajout du médicament : {e}")
        return False
    finally:
        conn.close()

def afficher_medicaments():
    
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nom, quantite, prix FROM medicaments")
    resultats = cursor.fetchall()

    if not resultats:
        print("Aucun médicament dans la base.")
    else:
        print("\n--- Liste des médicaments ---")
        for med in resultats:
            print(f"ID: {med[0]} | Nom: {med[1]} | Quantité: {med[2]} | Prix: {med[3]} €")

    conn.close()

def modifier_medicament(id, nom=None, quantite=None, prix=None):

    conn = connect_db()
    cursor = conn.cursor()

    # Construction dynamique de la requête SQL
    updates = []
    params = []
    if nom is not None:
        updates.append("nom = ?")
        params.append(nom)
    if quantite is not None:
        updates.append("quantite = ?")
        params.append(quantite)
    if prix is not None:
        updates.append("prix = ?")
        params.append(prix)

    if not updates:
        print("Aucun champ à modifier.")
        conn.close()
        return False

    query = f"UPDATE medicaments SET {', '.join(updates)} WHERE id = ?"
    params.append(id)

    try:
        cursor.execute(query, params)
        if cursor.rowcount == 0:
            print(f"Aucun médicament trouvé avec l'ID {id}.")
            return False
        conn.commit()
        print(f"Médicament ID {id} modifié avec succès.")
        return True
    except Exception as e:
        print(f"Erreur lors de la modification : {e}")
        return False
    finally:
        conn.close()

def supprimer_medicament(id):
   
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM medicaments WHERE id = ?", (id,))
        if cursor.rowcount == 0:
            print(f"Aucun médicament trouvé avec l'ID {id}.")
            return False
        conn.commit()
        print(f"Médicament ID {id} supprimé avec succès.")
        return True
    except sqlite3.IntegrityError:
        print(f"Erreur : Impossible de supprimer le médicament ID {id} car des ventes existent.")
        return False
    except Exception as e:
        print(f"Erreur lors de la suppression : {e}")
        return False
    finally:
        conn.close()

# --- GESTION DES CLIENTS ---

def ajouter_client(nom, prenom, naissance, phone=None, num_assurance=None):
    """
    Fonction pour ajouter un client dans la table clients.
    """
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO clients (nom, prenom, naissance, phone, num_assurance)
            VALUES (?, ?, ?, ?, ?)
        """, (nom, prenom, naissance, phone, num_assurance))
        conn.commit()
        print(f"Client '{prenom} {nom}' ajouté avec succès.")
        return True
    except Exception as e:
        print(f"Erreur lors de l'ajout du client : {e}")
        return False
    finally:
        conn.close()

def afficher_clients():
  
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nom, prenom FROM clients")
    resultats = cursor.fetchall()

    if not resultats:
        print("Aucun client dans la base.")
    else:
        print("\n--- Liste des clients ---")
        for cli in resultats:
            print(f"ID: {cli[0]} | Nom: {cli[1]} | Prénom: {cli[2]}")

    conn.close()

def modifier_client(id, nom=None, prenom=None, phone=None):
    
    conn = connect_db()
    cursor = conn.cursor()

    updates = []
    params = []
    if nom is not None:
        updates.append("nom = ?")
        params.append(nom)
    if prenom is not None:
        updates.append("prenom = ?")
        params.append(prenom)
    if phone is not None:
        updates.append("phone = ?")
        params.append(phone)

    if not updates:
        print("Aucun champ à modifier.")
        conn.close()
        return False

    query = f"UPDATE clients SET {', '.join(updates)} WHERE id = ?"
    params.append(id)

    try:
        cursor.execute(query, params)
        if cursor.rowcount == 0:
            print(f"Aucun client trouvé avec l'ID {id}.")
            return False
        conn.commit()
        print(f"Client ID {id} modifié avec succès.")
        return True
    except Exception as e:
        print(f"Erreur lors de la modification : {e}")
        return False
    finally:
        conn.close()

def supprimer_client(id):
   
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM clients WHERE id = ?", (id,))
        if cursor.rowcount == 0:
            print(f"Aucun client trouvé avec l'ID {id}.")
            return False
        conn.commit()
        print(f"Client ID {id} supprimé avec succès.")
        return True
    except Exception as e:
        print(f"Erreur lors de la suppression : {e}")
        return False
    finally:
        conn.close()

# --- GESTION DES VENTES ---

def enregistrer_vente(id_medicament, id_client, quantite, pharmacien="Inconnu"):
   
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Récupérer le prix du médicament
        cursor.execute("SELECT prix, quantite FROM medicaments WHERE id = ?", (id_medicament,))
        result = cursor.fetchone()
        if not result:
            print(f"Erreur : Médicament ID {id_medicament} introuvable.")
            return False

        prix_unitaire, stock_actuel = result
        if stock_actuel < quantite:
            print(f"Erreur : Stock insuffisant. Disponible: {stock_actuel}, demandé: {quantite}.")
            return False

        prix_total = prix_unitaire * quantite

        # Enregistrer la vente
        cursor.execute("""
            INSERT INTO vente (id_medicament, id_client, quantite, prix_unitaire, prix_total, pharmacien)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_medicament, id_client, quantite, prix_unitaire, prix_total, pharmacien))

        # Mettre à jour le stock
        cursor.execute("""
            UPDATE medicaments
            SET quantite = quantite - ?
            WHERE id = ?
        """, (quantite, id_medicament))

        conn.commit()
        print(f"Vente enregistrée : {quantite} x médicament ID {id_medicament} au client ID {id_client}.")
        return True
    except Exception as e:
        print(f"Erreur lors de l'enregistrement de la vente : {e}")
        return False
    finally:
        conn.close()

def afficher_ventes():
   
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT v.id, m.nom, c.nom, c.prenom, v.quantite, v.prix_total, v.date_vente
        FROM vente v
        LEFT JOIN medicaments m ON v.id_medicament = m.id
        LEFT JOIN clients c ON v.id_client = c.id
    """)
    resultats = cursor.fetchall()

    if not resultats:
        print("Aucune vente enregistrée.")
    else:
        print("\n--- Historique des ventes ---")
        for vente in resultats:
            print(f"ID: {vente[0]} | Médicament: {vente[1]} | Client: {vente[2]} {vente[3]} | Qté: {vente[4]} | Total: {vente[5]} € | Date: {vente[6]}")

    conn.close()

