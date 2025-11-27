import sqlite3
from datetime import datetime

DB = "pharmacie.db"

def connect_db():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# --- Helpers validation ---
def _is_valid_date(s):
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except Exception:
        return False

def _is_future_date(s):
    try:
        d = datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return False
    return d > datetime.today().date()


# MÉDICAMENTS

def ajouter_medicament(nom, code_barre, description, quantite, prix, date_expiration):
    # validations
    if not nom or not nom.strip():
        raise ValueError("Le nom du médicament ne peut pas être vide.")
    if not code_barre or not code_barre.strip():
        raise ValueError("Le code-barres ne peut pas être vide.")
    try:
        quantite = int(quantite)
    except Exception:
        raise ValueError("Quantité invalide.")
    try:
        prix = float(prix)
    except Exception:
        raise ValueError("Prix invalide.")

    if quantite < 0:
        raise ValueError("La quantité doit être >= 0.")
    if prix < 0:
        raise ValueError("Le prix doit être >= 0.")

    if date_expiration:
        if not _is_valid_date(date_expiration):
            raise ValueError("Format date d'expiration invalide (YYYY-MM-DD).")
        if not _is_future_date(date_expiration):
            raise ValueError("La date d'expiration doit être une date future.")

    conn = connect_db()
    cur = conn.cursor()
    # unicité code-barre
    cur.execute("SELECT id FROM medicaments WHERE code_barre = ?", (code_barre.strip(),))
    if cur.fetchone():
        conn.close()
        raise ValueError("Un médicament avec ce code-barres existe déjà.")

    try:
        cur.execute("""
            INSERT INTO medicaments (nom, code_barre, description, quantite, prix, date_expiration)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nom.strip(), code_barre.strip(), description or "", quantite, prix, date_expiration))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        raise ValueError("Erreur base de données (contrainte) : " + str(e))
    finally:
        conn.close()

def modifier_medicament(id_med, nom=None, quantite=None, prix=None, description=None, code_barre=None, date_expiration=None):
    # id check
    if id_med is None:
        raise ValueError("ID médicament requis.")
    try:
        id_med = int(id_med)
    except Exception:
        raise ValueError("ID médicament invalide.")

    # fetch existing to ensure exists
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id, code_barre FROM medicaments WHERE id = ?", (id_med,))
    existing = cur.fetchone()
    if not existing:
        conn.close()
        raise ValueError(f"Aucun médicament trouvé avec l'ID {id_med}.")

    # validations if provided
    if nom is not None and not nom.strip():
        conn.close()
        raise ValueError("Le nom ne peut pas être vide.")
    if code_barre is not None and not code_barre.strip():
        conn.close()
        raise ValueError("Le code-barres ne peut pas être vide.")

    if quantite is not None:
        try:
            quantite = int(quantite)
        except Exception:
            conn.close()
            raise ValueError("Quantité invalide.")
        if quantite < 0:
            conn.close()
            raise ValueError("Quantité doit être >= 0.")
    if prix is not None:
        try:
            prix = float(prix)
        except Exception:
            conn.close()
            raise ValueError("Prix invalide.")
        if prix < 0:
            conn.close()
            raise ValueError("Prix doit être >= 0.")
    if date_expiration:
        if not _is_valid_date(date_expiration):
            conn.close()
            raise ValueError("Format date d'expiration invalide (YYYY-MM-DD).")
        if not _is_future_date(date_expiration):
            conn.close()
            raise ValueError("La date d'expiration doit être future.")

    # check code_barre uniqueness if changed
    if code_barre is not None:
        cur.execute("SELECT id FROM medicaments WHERE code_barre = ? AND id != ?", (code_barre.strip(), id_med))
        if cur.fetchone():
            conn.close()
            raise ValueError("Ce code-barres est déjà utilisé par un autre médicament.")

    # build update dynamically (compatible avec appel depuis main)
    updates = []
    params = []
    if nom is not None:
        updates.append("nom = ?"); params.append(nom.strip())
    if code_barre is not None:
        updates.append("code_barre = ?"); params.append(code_barre.strip())
    if description is not None:
        updates.append("description = ?"); params.append(description)
    if quantite is not None:
        updates.append("quantite = ?"); params.append(quantite)
    if prix is not None:
        updates.append("prix = ?"); params.append(prix)
    if date_expiration is not None:
        updates.append("date_expiration = ?"); params.append(date_expiration)

    if not updates:
        conn.close()
        return True  # rien à faire

    params.append(id_med)
    q = f"UPDATE medicaments SET {', '.join(updates)} WHERE id = ?"
    try:
        cur.execute(q, params)
        if cur.rowcount == 0:
            conn.close()
            raise ValueError(f"Aucun médicament trouvé avec l'ID {id_med}.")
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        raise ValueError("Erreur base (contrainte) : " + str(e))
    finally:
        conn.close()

def supprimer_medicament(id_med):
    try:
        id_med = int(id_med)
    except Exception:
        raise ValueError("ID médicament invalide.")
    conn = connect_db()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM medicaments WHERE id = ?", (id_med,))
        if cur.rowcount == 0:
            conn.close()
            raise ValueError(f"Aucun médicament trouvé avec l'ID {id_med}.")
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError("Impossible de supprimer le médicament : des ventes existent liées.")
    finally:
        conn.close()


# CLIENTS

def ajouter_client(nom, prenom, naissance, phone=None, num_assurance=None):
    if not nom or not nom.strip():
        raise ValueError("Nom obligatoire.")
    if not prenom or not prenom.strip():
        raise ValueError("Prénom obligatoire.")
    if not naissance or not _is_valid_date(naissance):
        raise ValueError("Date de naissance invalide (YYYY-MM-DD).")
    if phone and phone.strip():
        p = phone.strip()
        if not (p.isdigit() or (p.startswith("+") and p[1:].isdigit())):
            raise ValueError("Téléphone invalide (chiffres ou +chiffres).")
        if len(p.replace("+","")) < 6:
            raise ValueError("Téléphone trop court.")
    if num_assurance and num_assurance.strip() and len(num_assurance.strip()) < 4:
        raise ValueError("Numéro d'assurance trop court (min 4 caractères).")

    conn = connect_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO clients (nom, prenom, naissance, phone, num_assurance)
            VALUES (?, ?, ?, ?, ?)
        """, (nom.strip(), prenom.strip(), naissance, (phone or "").strip(), (num_assurance or "").strip()))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        raise ValueError("Erreur base (contrainte) : " + str(e))
    finally:
        conn.close()

def modifier_client(id_cli, nom=None, prenom=None, naissance=None, phone=None, num_assurance=None):
    try:
        idc = int(id_cli)
    except Exception:
        raise ValueError("ID client invalide.")

    if nom is not None and not nom.strip():
        raise ValueError("Nom vide.")
    if prenom is not None and not prenom.strip():
        raise ValueError("Prénom vide.")
    if naissance is not None and not _is_valid_date(naissance):
        raise ValueError("Date de naissance invalide (YYYY-MM-DD).")
    if phone is not None and phone.strip():
        p = phone.strip()
        if not (p.isdigit() or (p.startswith("+") and p[1:].isdigit())):
            raise ValueError("Téléphone invalide.")
        if len(p.replace("+","")) < 6:
            raise ValueError("Téléphone trop court.")
    if num_assurance is not None and num_assurance.strip() and len(num_assurance.strip()) < 4:
        raise ValueError("Numéro d'assurance trop court.")

    conn = connect_db()
    cur = conn.cursor()
    updates = []; params = []
    if nom is not None:
        updates.append("nom = ?"); params.append(nom.strip())
    if prenom is not None:
        updates.append("prenom = ?"); params.append(prenom.strip())
    if naissance is not None:
        updates.append("naissance = ?"); params.append(naissance)
    if phone is not None:
        updates.append("phone = ?"); params.append(phone.strip())
    if num_assurance is not None:
        updates.append("num_assurance = ?"); params.append(num_assurance.strip())

    if not updates:
        conn.close()
        return True

    params.append(idc)
    q = f"UPDATE clients SET {', '.join(updates)} WHERE id = ?"
    try:
        cur.execute(q, params)
        if cur.rowcount == 0:
            conn.close()
            raise ValueError(f"Aucun client trouvé avec l'ID {idc}.")
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        raise ValueError("Erreur base (contrainte) : " + str(e))
    finally:
        conn.close()

def supprimer_client(id_cli):
    try:
        idc = int(id_cli)
    except Exception:
        raise ValueError("ID client invalide.")
    conn = connect_db()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM clients WHERE id = ?", (idc,))
        if cur.rowcount == 0:
            conn.close()
            raise ValueError(f"Aucun client trouvé avec l'ID {idc}.")
        conn.commit()
        return True
    finally:
        conn.close()


# VENTES

def enregistrer_vente(id_medicament, id_client, quantite, pharmacien="Inconnu"):
    # validations & conversions
    try:
        id_med = int(id_medicament)
    except Exception:
        raise ValueError("ID médicament invalide.")
    try:
        id_cli = int(id_client)
    except Exception:
        raise ValueError("ID client invalide.")
    try:
        qte = int(quantite)
    except Exception:
        raise ValueError("Quantité invalide.")
    if qte <= 0:
        raise ValueError("La quantité doit être > 0.")

    conn = connect_db()
    cur = conn.cursor()

    # vérifier médicament
    cur.execute("SELECT prix, quantite FROM medicaments WHERE id = ?", (id_med,))
    med = cur.fetchone()
    if not med:
        conn.close()
        raise ValueError("Médicament introuvable.")
    prix_unitaire, stock = med
    if stock < qte:
        conn.close()
        raise ValueError(f"Stock insuffisant. Disponible: {stock}, demandé: {qte}.")

    # vérifier client
    cur.execute("SELECT id FROM clients WHERE id = ?", (id_cli,))
    if not cur.fetchone():
        conn.close()
        raise ValueError("Client introuvable.")

    prix_total = prix_unitaire * qte

    try:
        cur.execute("""
            INSERT INTO vente (id_medicament, id_client, quantite, prix_unitaire, prix_total, pharmacien)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_med, id_cli, qte, prix_unitaire, prix_total, pharmacien))
        cur.execute("UPDATE medicaments SET quantite = quantite - ? WHERE id = ?", (qte, id_med))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        raise ValueError("Erreur base (contrainte) : " + str(e))
    finally:
        conn.close()

# Utilitaires d'affichage (lectures)
def fetch_medicaments():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id, nom, code_barre, quantite, prix, date_expiration FROM medicaments")
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_clients():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id, nom, prenom, naissance, phone, num_assurance FROM clients")
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_ventes():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT v.id, m.nom, c.nom, c.prenom, v.quantite, v.prix_total, v.date_vente
        FROM vente v
        LEFT JOIN medicaments m ON v.id_medicament = m.id
        LEFT JOIN clients c ON v.id_client = c.id
    """)
    rows = cur.fetchall()
    conn.close()
    return rows
