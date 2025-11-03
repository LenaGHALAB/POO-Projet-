import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import crud  
import db_phamarcie  

# Initialisation de la BD
db_phamarcie.create_table()


# Historique

historique_actions = []

def ajouter_historique(action):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    historique_actions.append(f"[{now}] {action}")
    refresh_historique()

# Interface principale 
root = tk.Tk()
root.title("Gestion de Pharmacie")
root.geometry("1200x650")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

frame_meds = ttk.Frame(notebook)
frame_clients = ttk.Frame(notebook)
frame_ventes = ttk.Frame(notebook)
frame_histo = ttk.Frame(notebook)

notebook.add(frame_meds, text="Médicaments")
notebook.add(frame_clients, text="Clients")
notebook.add(frame_ventes, text="Ventes")
notebook.add(frame_histo, text="Historique")


# MÉDICAMENTS 


def afficher_medicaments():
    meds_tree.delete(*meds_tree.get_children())
    conn = crud.connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id, nom, code_barre, quantite, prix, date_expiration FROM medicaments")
    for row in cur.fetchall():
        meds_tree.insert("", "end", values=row)
    conn.close()

def ajouter_medicament():
    try:
        nom = entry_nom.get()
        code = entry_code.get()
        desc = entry_desc.get()
        prix = float(entry_prix.get())
        qte = int(entry_qte.get())
        date_exp = entry_date.get()
        res = crud.ajouter_medicament(nom, code, desc, qte, prix, date_exp)
        if res:
            messagebox.showinfo("Succès", f"Médicament '{nom}' ajouté.")
            ajouter_historique(f"Ajout médicament: {nom}")
            afficher_medicaments()
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

def supprimer_medicament():
    selected = meds_tree.focus()
    if not selected:
        messagebox.showwarning("Sélection requise", "Sélectionnez un médicament.")
        return
    id_med = meds_tree.item(selected)["values"][0]
    crud.supprimer_medicament(id_med)
    ajouter_historique(f"Suppression médicament ID {id_med}")
    afficher_medicaments()

def remplir_champs_medicament(event):
    selected = meds_tree.focus()
    if not selected:
        return
    values = meds_tree.item(selected)["values"]
    entry_nom_mod.delete(0, tk.END)
    entry_nom_mod.insert(0, values[1])
    entry_qte_mod.delete(0, tk.END)
    entry_qte_mod.insert(0, values[3])
    entry_prix_mod.delete(0, tk.END)
    entry_prix_mod.insert(0, values[4])

def modifier_medicament():
    selected = meds_tree.focus()
    if not selected:
        messagebox.showwarning("Sélection requise", "Sélectionnez un médicament.")
        return
    id_med = meds_tree.item(selected)["values"][0]
    nom = entry_nom_mod.get() or None
    quantite = int(entry_qte_mod.get()) if entry_qte_mod.get() else None
    prix = float(entry_prix_mod.get()) if entry_prix_mod.get() else None
    crud.modifier_medicament(id_med, nom, quantite, prix)
    ajouter_historique(f"Modification médicament ID {id_med}")
    afficher_medicaments()

# Interface médicaments
frm_top = ttk.LabelFrame(frame_meds, text="Ajouter un médicament")
frm_top.pack(fill="x", padx=10, pady=5)

tk.Label(frm_top, text="Nom:").grid(row=0, column=0)
tk.Label(frm_top, text="Code-barre:").grid(row=0, column=2)
tk.Label(frm_top, text="Description:").grid(row=1, column=0)
tk.Label(frm_top, text="Prix:").grid(row=1, column=2)
tk.Label(frm_top, text="Quantité:").grid(row=2, column=0)
tk.Label(frm_top, text="Expiration:").grid(row=2, column=2)

entry_nom = tk.Entry(frm_top)
entry_code = tk.Entry(frm_top)
entry_desc = tk.Entry(frm_top)
entry_prix = tk.Entry(frm_top)
entry_qte = tk.Entry(frm_top)
entry_date = tk.Entry(frm_top)

entry_nom.grid(row=0, column=1)
entry_code.grid(row=0, column=3)
entry_desc.grid(row=1, column=1)
entry_prix.grid(row=1, column=3)
entry_qte.grid(row=2, column=1)
entry_date.grid(row=2, column=3)

tk.Button(frm_top, text="Ajouter", command=ajouter_medicament).grid(row=3, column=0, pady=5)
tk.Button(frm_top, text="Supprimer", command=supprimer_medicament).grid(row=3, column=1)
tk.Button(frm_top, text="Actualiser", command=afficher_medicaments).grid(row=3, column=2)

# Tableau des médicaments
cols = ("ID", "Nom", "Code-barre", "Quantité", "Prix", "Expiration")
meds_tree = ttk.Treeview(frame_meds, columns=cols, show="headings")
for c in cols:
    meds_tree.heading(c, text=c)
    meds_tree.column(c, width=150)
meds_tree.pack(fill="both", expand=True, padx=10, pady=5)
meds_tree.bind("<<TreeviewSelect>>", remplir_champs_medicament)

frm_mod = ttk.LabelFrame(frame_meds, text="Modifier le médicament sélectionné")
frm_mod.pack(fill="x", padx=10, pady=5)
tk.Label(frm_mod, text="Nom:").grid(row=0, column=0)
tk.Label(frm_mod, text="Quantité:").grid(row=0, column=2)
tk.Label(frm_mod, text="Prix :").grid(row=0, column=4)
entry_nom_mod = tk.Entry(frm_mod)
entry_qte_mod = tk.Entry(frm_mod)
entry_prix_mod = tk.Entry(frm_mod)
entry_nom_mod.grid(row=0, column=1)
entry_qte_mod.grid(row=0, column=3)
entry_prix_mod.grid(row=0, column=5)
tk.Button(frm_mod, text="Modifier", command=modifier_medicament).grid(row=0, column=6, padx=5)


# CLIENTS 


def afficher_clients():
    clients_tree.delete(*clients_tree.get_children())
    conn = crud.connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id, nom, prenom, phone FROM clients")
    for row in cur.fetchall():
        clients_tree.insert("", "end", values=row)
    conn.close()

def ajouter_client():
    nom = entry_c_nom.get()
    prenom = entry_c_prenom.get()
    naissance = entry_c_naiss.get()
    phone = entry_c_phone.get()
    num_assurance = entry_c_assu.get()
    crud.ajouter_client(nom, prenom, naissance, phone, num_assurance)
    ajouter_historique(f"Ajout client: {prenom} {nom}")
    afficher_clients()

def supprimer_client():
    selected = clients_tree.focus()
    if not selected:
        messagebox.showwarning("Sélection requise", "Sélectionnez un client.")
        return
    id_cli = clients_tree.item(selected)["values"][0]
    crud.supprimer_client(id_cli)
    ajouter_historique(f"Suppression client ID {id_cli}")
    afficher_clients()

def remplir_champs_client(event):
    selected = clients_tree.focus()
    if not selected:
        return
    values = clients_tree.item(selected)["values"]
    entry_c_nom_mod.delete(0, tk.END)
    entry_c_nom_mod.insert(0, values[1])
    entry_c_prenom_mod.delete(0, tk.END)
    entry_c_prenom_mod.insert(0, values[2])
    entry_c_phone_mod.delete(0, tk.END)
    entry_c_phone_mod.insert(0, values[3])

def modifier_client():
    selected = clients_tree.focus()
    if not selected:
        messagebox.showwarning("Sélection requise", "Sélectionnez un client.")
        return
    id_cli = clients_tree.item(selected)["values"][0]
    nom = entry_c_nom_mod.get() or None
    prenom = entry_c_prenom_mod.get() or None
    phone = entry_c_phone_mod.get() or None
    crud.modifier_client(id_cli, nom, prenom, phone)
    ajouter_historique(f"Modification client ID {id_cli}")
    afficher_clients()

# Interface client
frm_c = ttk.LabelFrame(frame_clients, text="Ajouter un client")
frm_c.pack(fill="x", padx=10, pady=5)
for i, lbl in enumerate(["Nom", "Prénom", "Naissance", "Téléphone", "Assurance"]):
    tk.Label(frm_c, text=f"{lbl}:").grid(row=i//2, column=(i%2)*2)
entries = [tk.Entry(frm_c) for _ in range(5)]
entry_c_nom, entry_c_prenom, entry_c_naiss, entry_c_phone, entry_c_assu = entries
entry_c_nom.grid(row=0, column=1)
entry_c_prenom.grid(row=0, column=3)
entry_c_naiss.grid(row=1, column=1)
entry_c_phone.grid(row=1, column=3)
entry_c_assu.grid(row=2, column=1)

tk.Button(frm_c, text="Ajouter", command=ajouter_client).grid(row=3, column=0, pady=5)
tk.Button(frm_c, text="Supprimer", command=supprimer_client).grid(row=3, column=1)
tk.Button(frm_c, text="Actualiser", command=afficher_clients).grid(row=3, column=2)

# Tableau client
cols_c = ("ID", "Nom", "Prénom", "Téléphone")
clients_tree = ttk.Treeview(frame_clients, columns=cols_c, show="headings")
for c in cols_c:
    clients_tree.heading(c, text=c)
    clients_tree.column(c, width=180)
clients_tree.pack(fill="both", expand=True, padx=10, pady=5)
clients_tree.bind("<<TreeviewSelect>>", remplir_champs_client)

frm_mod_c = ttk.LabelFrame(frame_clients, text="Modifier le client sélectionné")
frm_mod_c.pack(fill="x", padx=10, pady=5)
tk.Label(frm_mod_c, text="Nom:").grid(row=0, column=0)
tk.Label(frm_mod_c, text="Prénom:").grid(row=0, column=2)
tk.Label(frm_mod_c, text="Téléphone:").grid(row=0, column=4)
entry_c_nom_mod = tk.Entry(frm_mod_c)
entry_c_prenom_mod = tk.Entry(frm_mod_c)
entry_c_phone_mod = tk.Entry(frm_mod_c)
entry_c_nom_mod.grid(row=0, column=1)
entry_c_prenom_mod.grid(row=0, column=3)
entry_c_phone_mod.grid(row=0, column=5)
tk.Button(frm_mod_c, text="Modifier", command=modifier_client).grid(row=0, column=6, padx=5)



#  VENTES 


def afficher_ventes():
    for row in ventes_tree.get_children():
        ventes_tree.delete(row)
    conn = crud.connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT v.id, m.nom, c.nom, c.prenom, v.quantite, v.prix_total, v.date_vente
        FROM vente v
        LEFT JOIN medicaments m ON v.id_medicament = m.id
        LEFT JOIN clients c ON v.id_client = c.id
    """)
    rows = cur.fetchall()
    for r in rows:
        ventes_tree.insert("", "end", values=r)
    conn.close()

def enregistrer_vente():
    try:
        id_med = int(entry_v_med.get())
        id_cli = int(entry_v_cli.get())
        qte = int(entry_v_qte.get())
        pharma = entry_v_pharma.get() or "Inconnu"
        res = crud.enregistrer_vente(id_med, id_cli, qte, pharma)
        if res:
            messagebox.showinfo("Succès", "Vente enregistrée.")
            ajouter_historique(f"Vente enregistrée (médicament {id_med}, client {id_cli}, qté {qte})")
            afficher_ventes()
            afficher_medicaments()
        else:
            messagebox.showerror("Erreur", "Échec lors de la vente.")
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

# Interface ventes
frm_v = ttk.LabelFrame(frame_ventes, text="Nouvelle vente")
frm_v.pack(fill="x", padx=10, pady=5)

tk.Label(frm_v, text="ID Médicament:").grid(row=0, column=0)
tk.Label(frm_v, text="ID Client:").grid(row=0, column=2)
tk.Label(frm_v, text="Quantité:").grid(row=1, column=0)
tk.Label(frm_v, text="Pharmacien:").grid(row=1, column=2)

entry_v_med = tk.Entry(frm_v)
entry_v_cli = tk.Entry(frm_v)
entry_v_qte = tk.Entry(frm_v)
entry_v_pharma = tk.Entry(frm_v)

entry_v_med.grid(row=0, column=1)
entry_v_cli.grid(row=0, column=3)
entry_v_qte.grid(row=1, column=1)
entry_v_pharma.grid(row=1, column=3)

tk.Button(frm_v, text="Enregistrer vente", command=enregistrer_vente).grid(row=2, column=0, columnspan=4, pady=5)

# Tableau ventes
cols_v = ("ID", "Médicament", "Nom Client", "Prénom", "Quantité", "Total", "Date")
ventes_tree = ttk.Treeview(frame_ventes, columns=cols_v, show="headings")
for c in cols_v:
    ventes_tree.heading(c, text=c)
    ventes_tree.column(c, width=150)
ventes_tree.pack(fill="both", expand=True, padx=10, pady=5)

tk.Button(frame_ventes, text="Actualiser", command=afficher_ventes).pack(pady=5)



# HISTORIQUE 


historique_listbox = tk.Listbox(frame_histo, font=("Consolas", 10))
historique_listbox.pack(fill="both", expand=True, padx=10, pady=10)

def refresh_historique():
    historique_listbox.delete(0, tk.END)
    for item in historique_actions:
        historique_listbox.insert(tk.END, item)

# Chargement initial
afficher_medicaments()
afficher_clients()
afficher_ventes()

root.mainloop()
