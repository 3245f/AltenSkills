
# app.py
from flask import Flask, request, render_template, send_file, abort, redirect, url_for
import pandas as pd
import os
from datetime import datetime
import threading # Importa il modulo threading per la gestione della concorrenza

app = Flask(__name__)

EXCEL_FILE = "alten_skills_trial.xlsx"
USER_FILES_DIR = "skills_user"

# Crea un oggetto Lock per gestire l'accesso concorrente al file Excel principale
excel_lock = threading.Lock()

# Assicurati che la directory per i file utente esista
os.makedirs(USER_FILES_DIR, exist_ok=True)

# Assicurati che il file Excel principale esista con le intestazioni appropriate
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=[
        "ID", "Nome", "Email", "Istruzione", "Indirizzo di studio", "Sede Alten",
        "Esperienza (anni)", "Esperienza Alten (anni)", "Certificazioni",
        "Clienti Railway", "Area Railway", "Normative", "Metodologie lavoro",
        "Sistemi Operativi", "Info aggiuntive", "Hobby"
        # Aggiungi qui le altre colonne dinamiche che potrebbero essere create
    ])
    df.to_excel(EXCEL_FILE, index=False)
    print(f"File Excel '{EXCEL_FILE}' creato con successo.")
else:
    print(f"File Excel '{EXCEL_FILE}' già esistente.")

## Assegnazione di un nuovo ID a ciascun nuovo utente che compila il Form
def get_next_id():
    """Genera il prossimo ID disponibile per un nuovo utente."""
    # Acquisisce il lock per assicurarsi che la lettura del file sia atomica
    with excel_lock:
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE)
            if not df.empty and "ID" in df.columns:
                return df["ID"].max() + 1
    return 1

# La funzione per rimuovere l'utente dal file principale è stata disabilitata come richiesto.
# def remove_user_from_main_file(user_id):
#     """
#     QUESTA FUNZIONE È STATA TEMPORANEAMENTE RIMOSSA.
#     Rimuove la riga dal file principale basata sull'ID dell'utente.
#     """
#     with excel_lock: # Acquisisce il lock anche per la cancellazione
#         if os.path.exists(EXCEL_FILE):
#             df = pd.read_excel(EXCEL_FILE)
#             df = df[df["ID"] != user_id]
#             df.to_excel(EXCEL_FILE, index=False)

# Funzione per aggiungere le informazioni in ordine logico
def aggiungi_sezione(nome_sezione, scelte, dettagli_dict, data):
    """Aggiunge la colonna con le scelte e i dettagli di una specifica area al dizionario dei dati."""
    data[f"Aree progetti {nome_sezione}"] = ", ".join(scelte)
    
    # Aggiunge la colonna con i dettagli subito dopo la relativa sezione
    for area in dettagli_dict:
        # Assicurati che la chiave sia presente prima di accedervi per evitare KeyError
        if area in dettagli_dict:
            data[area] = "\n\n".join(dettagli_dict[area]) if dettagli_dict[area] else ""
        else:
            data[area] = "" # Inizializza con stringa vuota se l'area non ha dettagli

@app.route("/", methods=["GET", "POST"])
def index():
    """Gestisce l'invio del form e il salvataggio dei dati."""
    success_message = None
    show_delete_button = False # Il pulsante di eliminazione è sempre nascosto
    user_id = None  # Variabile per salvare l'ID dell'utente
    user_filename = None

    if request.method == "POST":
        user_id = get_next_id() # Preleva il prossimo ID disponibile

        # Preleva i dati dal form
        nome = request.form.get("nome", "")
        email = request.form.get("email", "")
        istruzione = request.form.get("istruzione", "")
        studi = request.form.get("studi", "")
        certificati = request.form.get("certificati", "")
        sede = request.form.get("sede", "")
        esperienza = request.form.get("esperienza", "")
        esperienza_alten = request.form.get("esperienza_alten", "")
        clienti_railway = request.form.getlist("clienti")
        clienti_str = ", ".join(clienti_railway) if clienti_railway else ""
        area_railway = request.form.getlist("area_railway")
        area_str = ", ".join(area_railway) if area_railway else ""
        normative = request.form.get("normative", "")
        metodologia = request.form.getlist("metodologia")
        metodologia_str = ", ".join(metodologia) if metodologia else ""
        sistemi_operativi = request.form.get("SistemiOperativi", "")
        altro = request.form.getlist("altro")
        altro_str = ", ".join(altro) if altro else ""
        hobby = request.form.getlist("hobby")
        hobby_str = ", ".join(hobby) if hobby else ""

        # --- Progetti SVILUPPO ---
        scelte_progetti_sviluppo = request.form.getlist('sviluppo')
        dettagli_sviluppo = {area: [] for area in ["Applicativi", "Firmware", "Web", "Mobile", "Scada", "Plc"]}
        for area in dettagli_sviluppo.keys():
            if area not in scelte_progetti_sviluppo:
                continue
            linguaggi = request.form.getlist(f'linguaggi_{area.lower()}[]')
            tool = request.form.getlist(f'tool_{area.lower()}[]')
            ambito = request.form.getlist(f'Ambito_{area.lower()}[]')
            durata = request.form.getlist(f'durata_{area.lower()}[]')
            descrizione = request.form.getlist(f'descrizione_{area.lower()}[]')
            esperienze = []
            max_len = max(len(linguaggi), len(tool), len(ambito), len(durata), len(descrizione))
            for i in range(max_len):
                l = linguaggi[i] if i < len(linguaggi) else ""
                t = tool[i] if i < len(tool) else ""
                a = ambito[i] if i < len(ambito) else ""
                e = durata[i] if i < len(durata) else ""
                d = descrizione[i] if i < len(descrizione) else ""
                esperienze.append(f"{l} | {t} | {a} | {e} | {d}")
            dettagli_sviluppo[area] = esperienze

        # --- Progetti V&V ---
        scelte_progetti_vv = request.form.getlist('v&v')
        dettagli_vv = {area: [] for area in ["functional_testing", "test_and_commisioning", "unit", "analisi_statica", "analisi_dinamica", "automatic_test", "piani_schematici", "procedure", "cablaggi", "FAT", "SAT", "doc"]}
        for area in dettagli_vv.keys():
            if area not in scelte_progetti_vv:
                continue
            tecnologie = request.form.getlist(f'tecnologie_{area}[]')
            ambito = request.form.getlist(f'azienda_{area}[]')
            durata = request.form.getlist(f'durata_{area}[]')
            descrizione = request.form.getlist(f'descrizione_{area}[]')
            esperienze = []
            max_len = max(len(tecnologie), len(ambito), len(durata), len(descrizione))
            for i in range(max_len):
                t = tecnologie[i] if i < len(tecnologie) else ""
                a = ambito[i] if i < len(ambito) else ""
                e = durata[i] if i < len(durata) else ""
                d = descrizione[i] if i < len(descrizione) else ""
                esperienze.append(f"{t} | {a} | {e} | {d}")
            dettagli_vv[area] = esperienze
        
        # --- Progetti System ---
        scelte_progetti_system = request.form.getlist('system')
        dettagli_system = {area: [] for area in ["requirement_management", "requirement_engineering", "system_engineering", "project_engineering"]}
        for area in dettagli_system.keys():
            if area not in scelte_progetti_system:
                continue
            tecnologie = request.form.getlist(f'tecnologie_{area}[]')
            ambito = request.form.getlist(f'azienda_{area}[]')
            durata = request.form.getlist(f'durata_{area}[]')
            descrizione = request.form.getlist(f'descrizione_{area}[]')
            esperienze = []
            max_len = max(len(tecnologie), len(ambito), len(durata), len(descrizione))
            for i in range(max_len):
                t = tecnologie[i] if i < len(tecnologie) else ""
                a = ambito[i] if i < len(ambito) else ""
                e = durata[i] if i < len(durata) else ""
                d = descrizione[i] if i < len(descrizione) else ""
                esperienze.append(f"{t} | {a} | {e} | {d}")
            dettagli_system[area] = esperienze

        # --- Progetti Safety ---
        scelte_progetti_safety = request.form.getlist('safety')
        dettagli_safety = {area: [] for area in ["RAMS", "hazard_analysis", "verification_report", "fire_safety", "reg_402"]}
        for area in dettagli_safety.keys():
            if area not in scelte_progetti_safety:
                continue
            tecnologie = request.form.getlist(f'tecnologie_{area}[]')
            ambito = request.form.getlist(f'azienda_{area}[]')
            durata = request.form.getlist(f'durata_{area}[]')
            descrizione = request.form.getlist(f'descrizione_{area}[]')
            esperienze = []
            max_len = max(len(tecnologie), len(ambito), len(durata), len(descrizione))
            for i in range(max_len):
                t = tecnologie[i] if i < len(tecnologie) else ""
                a = ambito[i] if i < len(ambito) else ""
                e = durata[i] if i < len(durata) else ""
                d = descrizione[i] if i < len(descrizione) else ""
                esperienze.append(f"{t} | {a} | {e} | {d}")
            dettagli_safety[area] = esperienze

        # --- Progetti Segnalamento ---
        scelte_progetti_segnalamento = request.form.getlist('segnalamento')
        dettagli_seg = {area: [] for area in ["piani_schematici_segnalamento", "cfg_impianti", "layout_apparecchiature", "architettura_rete", "computo_metrico"]}
        for area in dettagli_seg.keys():
            if area not in scelte_progetti_segnalamento:
                continue
            tecnologie = request.form.getlist(f'tecnologie_{area}[]')
            ambito = request.form.getlist(f'azienda_{area}[]')
            durata = request.form.getlist(f'durata_{area}[]')
            descrizione = request.form.getlist(f'descrizione_{area}[]')
            esperienze = []
            max_len = max(len(tecnologie), len(ambito), len(durata), len(descrizione))
            for i in range(max_len):
                t = tecnologie[i] if i < len(tecnologie) else ""
                a = ambito[i] if i < len(ambito) else ""
                e = durata[i] if i < len(durata) else ""
                d = descrizione[i] if i < len(descrizione) else ""
                esperienze.append(f"{t} | {a} | {e} | {d}")
            dettagli_seg[area] = esperienze

        # --- Progetti BIM ---
        scelte_progetti_bim = request.form.getlist('bim')
        dettagli_bim = {area: [] for area in ["modellazione_e_digitalizzazione", "verifica_analisi_e_controllo_qualita", "gestione_coordinamento_e_simulazione", "visualizzazione_realtavirtuale_e_rendering"]}
        for area in dettagli_bim.keys():
            if area not in scelte_progetti_bim:
                continue
            tool = request.form.getlist(f'tool_{area}[]')
            azienda = request.form.getlist(f'azienda_{area}[]')
            durata = request.form.getlist(f'durata_{area}[]')
            descrizione = request.form.getlist(f'descrizione_{area}[]')
            certificazione = request.form.getlist(f'certificazioni_{area}[]')
            esperienze = []
            max_len = max(len(certificazione), len(tool), len(azienda), len(descrizione), len(durata))
            for i in range(max_len):
                t = tool[i] if i < len(tool) else ""
                a = azienda[i] if i < len(azienda) else ""
                e = durata[i] if i < len(durata) else ""
                d = descrizione[i] if i < len(descrizione) else ""
                c = certificazione[i] if i < len(certificazione) else ""
                esperienze.append(f"{t} | {a} | {e} | {d} | {c}")
            dettagli_bim[area] = esperienze

        # --- Progetti PM ---
        scelte_progetti_pm = request.form.getlist('pm')
        dettagli_pm = {area: [] for area in ["project_manager_office", "project_manager", "risk_manager", "resource_manager", "quality_manager", "communication_manager", "portfolio_manager", "program_manager","team_leader", "business_analyst", "contract_back_office"]}
        for area in dettagli_pm.keys():
            if area not in scelte_progetti_pm:
                continue
            tool = request.form.getlist(f'tool_{area}[]')
            azienda = request.form.getlist(f'azienda_{area}[]')
            durata = request.form.getlist(f'durata_{area}[]')
            descrizione = request.form.getlist(f'descrizione_{area}[]')
            esperienze = []
            max_len = max(len(tool), len(azienda), len(durata), len(descrizione))
            for i in range(max_len):
                t = tool[i] if i < len(tool) else ""
                a = azienda[i] if i < len(azienda) else ""
                e = durata[i] if i < len(durata) else ""
                d = descrizione[i] if i < len(descrizione) else ""
                esperienze.append(f"{t} | {a} | {e} | {d}")
            dettagli_pm[area] = esperienze

        # Dati da salvare nel file excel
        data = {
            "ID": user_id,
            "Nome": nome,
            "Email": email,
            "Istruzione": istruzione,
            "Indirizzo di studio": studi,
            "Sede Alten": sede,
            "Esperienza (anni)": esperienza,
            "Esperienza Alten (anni)": esperienza_alten,
            "Certificazioni": certificati,
            "Clienti Railway": clienti_str,
            "Area Railway": area_str,
            "Normative": normative,
            "Metodologie lavoro": metodologia_str,
            "Sistemi Operativi": sistemi_operativi,
            "Info aggiuntive": altro_str,
            "Hobby": hobby_str,
        }

        # Aggiunta delle varie sezioni con i dettagli in ordine
        aggiungi_sezione("Sviluppo", scelte_progetti_sviluppo, dettagli_sviluppo, data)
        aggiungi_sezione("V&V", scelte_progetti_vv, dettagli_vv, data)
        aggiungi_sezione("Safety", scelte_progetti_safety, dettagli_safety, data)
        aggiungi_sezione("System", scelte_progetti_system, dettagli_system, data)
        aggiungi_sezione("Segnalamento", scelte_progetti_segnalamento, dettagli_seg, data)
        aggiungi_sezione("BIM", scelte_progetti_bim, dettagli_bim, data)
        aggiungi_sezione("Project Management", scelte_progetti_pm, dettagli_pm, data)

        # Salvataggio dei dati nel file Excel principale
        if request.form['action'] == 'submit_main':
            try:
                # Acquisisce il blocco prima di leggere/scrivere il file Excel principale
                with excel_lock:
                    print(f"Lock acquisito per la scrittura del file Excel principale.")
                    df = pd.read_excel(EXCEL_FILE)
                    # Aggiunge nuove colonne se non esistono, per evitare errori KeyError
                    for col in data.keys():
                        if col not in df.columns:
                            df[col] = ''
                    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
                    df.to_excel(EXCEL_FILE, index=False)
                    print(f"Dati scritti sul file Excel principale. Lock rilasciato.")
                success_message = "Risposte inviate con successo!" # Messaggio di successo

                ####################### Salvataggio del file con le risposte del singolo utente ####################
                # Questo file non necessita del lock, poiché è un file nuovo e non condiviso.
                user_df_single = pd.DataFrame([data])
                # Rimuove la colonna 'ID' solo se esiste per il file utente
                if 'ID' in user_df_single.columns:
                    user_df_single = user_df_single.drop(columns=["ID"])

                user_filename = f"skills_{datetime.now().strftime('%Y%m%d%H%M%S')}_{user_id}.xlsx"
                print("user_file_name", user_filename)
                user_filepath = os.path.join(USER_FILES_DIR, user_filename)
                print(user_filepath)
                # Salvataggio del file personale
                user_df_single.to_excel(user_filepath, index=False)

            except Exception as e:
                success_message = f'Si è verificato un errore durante l\'invio delle risposte: {e}' # Messaggio di errore
                print(f"Errore: {e}") # Stampa l'errore per il debug

        # La funzionalità di eliminazione è stata rimossa come richiesto.
        # Le seguenti righe sono state commentate per disabilitare la logica di eliminazione.
        # elif request.form['action'] == 'delete_from_main' and user_id:
        #     print(user_id)
        #     remove_user_from_main_file(user_id - 1)
        #     success_message = "Risposta eliminata dal file principale!"
        #     show_delete_button = False

    return render_template("form.html", success_message=success_message, show_delete_button=show_delete_button, user_filename=user_filename)

@app.route("/download")
def download():
    """Consente il download del file Excel principale o di un file utente specifico."""
    file_type = request.args.get("file", "main")  # Valore di default: 'main'

    if file_type == "personal":
        filename = request.args.get("filename")  # Il nome del file personale
        if not filename:
            abort(400, description="Missing filename parameter")
        
        user_filepath = os.path.join(USER_FILES_DIR, filename)
        if not os.path.exists(user_filepath):
            abort(404, description="File not found")

        return send_file(user_filepath, as_attachment=True, download_name=filename)
    
    # Per il download del file principale, è buona norma acquisire il lock per assicurare
    # che si legga uno stato consistente del file, anche se meno critico di una scrittura.
    try:
        with excel_lock:
            if not os.path.exists(EXCEL_FILE):
                abort(404, description="File not found")
            return send_file(EXCEL_FILE, as_attachment=True, download_name="skills_trial.xlsx")
    except Exception as e:
        # Quando flash non è usato, si può passare il messaggio direttamente al template o reindirizzare con un messaggio
        print(f'Si è verificato un errore durante il download del file: {e}')
        return redirect(url_for('index')) # Reindirizza e l'utente dovrà verificare la console per l'errore

if __name__ == "__main__":
    # In un ambiente di produzione reale, è consigliabile utilizzare un server WSGI
    # come Gunicorn o uWSGI anziché app.run(debug=True) per la gestione della concorrenza.
    # Tuttavia, per lo sviluppo e test, debug=True va bene.
    app.run(debug=True)
