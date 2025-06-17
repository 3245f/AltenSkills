from flask import Flask, request, render_template, send_file, abort, redirect, url_for
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

EXCEL_FILE = "skills_trial.xlsx"

USER_FILES_DIR = "skills_user"
os.makedirs(USER_FILES_DIR, exist_ok=True)



user_df = pd.DataFrame(columns=[
         "Nome", "Email"])

if not os.path.exists(EXCEL_FILE):


    df = pd.DataFrame(columns=[
        "ID", "Nome", "Email"])

    df.to_excel(EXCEL_FILE, index=False)


## assegnazione di un nuovo ID a ciascun nuovo utente che compila il Form
def get_next_id():
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        if not df.empty:
            return df["ID"].max() + 1
    return 1



def remove_user_from_main_file(user_id):
    # Rimuovi la riga dal file principale basata sull'ID dell'utente
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        # Trova e rimuovi la riga corrispondente all'ID dell'utente
        df = df[df["ID"] != user_id]
        df.to_excel(EXCEL_FILE, index=False)




# Funzione per aggiungere le informazioni in ordine logico
def aggiungi_sezione(nome_sezione, scelte, dettagli_dict,data):
    """Aggiunge la colonna con le scelte e i dettagli di una specifica area al dizionario dei dati"""
    data[f"Aree progetti {nome_sezione}"] = ", ".join(scelte)
    
    # Aggiunge la colonna con i dettagli subito dopo la relativa sezione
    for area in dettagli_dict:
        data[area] = "\n\n".join(dettagli_dict[area]) if dettagli_dict[area] else ""
       

@app.route("/", methods=["GET", "POST"])
def index():

    success_message = None
    show_delete_button = False
    user_id = None  # Variabile per salvare l'ID dell'utente
    user_filename = None
    if request.method == "POST":

        #preleva i dati dal form
        user_id = get_next_id()
        nome = request.form.get("nome", "")
        email = request.form.get("email", "")
        istruzione = request.form.get("istruzione", "")
        studi = request.form.get("studi", "")
        certificati = request.form.get("certificati", "")
        sede = request.form.get("sede", "")
        esperienza = request.form.get("esperienza", "")
        esperienza_alten = request.form.get("esperienza_alten", "")
        clienti_railway= request.form.getlist("clienti")  
        clienti_str = ", ".join(clienti_railway) if clienti_railway else "" 
        area_railway= request.form.getlist("area_railway")  
        area_str = ", ".join(area_railway) if area_railway else "" 
        normative = request.form.get("normative", "")
        metodologia= request.form.getlist("metodologia")  
        metodologia_str = ", ".join(metodologia) if metodologia else "" 
        sistemi_operativi = request.form.get("SistemiOperativi", "")
        altro= request.form.getlist("altro")  
        altro_str = ", ".join(altro) if altro else "" 
        hobby= request.form.getlist("hobby")  
        hobby_str = ", ".join(hobby) if hobby else "" 


# Progetti SVILUPPO
        progetti_sviluppo_si_no = request.form.get('progetti_sw_hw_auto', 'No')  
        scelte_progetti_sviluppo = request.form.getlist('sviluppo')  
        dettagli_sviluppo = {area: "" for area in ["Applicativi", "Firmware", "Web", "Mobile", "Scada", "Plc"]}
        for area in dettagli_sviluppo.keys():
            if area not in scelte_progetti_sviluppo:  
                continue  

            linguaggi = request.form.getlist(f'linguaggi_{area.lower()}[]')
            tool = request.form.getlist(f'tool_{area.lower()}[]')
            ambito = request.form.getlist(f'Ambito_{area.lower()}[]')
            durata = request.form.getlist(f'durata_{area.lower()}[]')
            descrizione = request.form.getlist(f'descrizione_{area.lower()}[]')
            #print(f"{area} -> Linguaggi: {linguaggi}, Tool: {tool}, Ambito: {ambito}, Durata: {durata}, Descrizione: {descrizione}")
            esperienze = []
            for i in range(max(len(linguaggi), len(tool), len(ambito), len(durata), len(descrizione))):
                l = linguaggi[i] if i < len(linguaggi) else ""
                t = tool[i] if i < len(tool) else ""
                a = ambito[i] if i < len(ambito) else ""
                e = durata[i] if i < len(durata) else ""
                d = descrizione[i] if i < len(descrizione) else ""
                esperienze.append(f"{l} | {t} | {a} | {e} | {d}")
            dettagli_sviluppo[area] =esperienze

      
# Progetti V&V
        scelte_progetti_vv = request.form.getlist('v&v')  
        dettagli_vv = {area: "" for area in ["functional_testing", "test_and_commisioning", "unit", "analisi_statica", "analisi_dinamica", "automatic_test", "piani_schematici", "procedure", "cablaggi", "FAT", "SAT", "doc"]}
        for area in dettagli_vv.keys():
            if area not in scelte_progetti_vv:  
                continue  

            tecnologie = request.form.getlist(f'tecnologie_{area}[]')
            ambito = request.form.getlist(f'azienda_{area}[]')
            durata = request.form.getlist(f'durata_{area}[]')
            descrizione = request.form.getlist(f'descrizione_{area}[]')
            #print(f"{area} -> Tecnologie: {tecnologie}, Ambito: {ambito}, Durata: {durata}, Descrizione: {descrizione}")
            esperienze = []
            for i in range(max(len(tecnologie), len(ambito), len(descrizione))):
                t = tecnologie[i] if i < len(tecnologie) else ""
                a = ambito[i] if i < len(ambito) else ""
                e = durata[i] if i < len(durata) else ""
                d = descrizione[i] if i < len(descrizione) else ""
                esperienze.append(f" {t} | {a} | {e} | {d}")
            dettagli_vv[area] =esperienze
       
# Progetti System
        scelte_progetti_system = request.form.getlist('system')  
        dettagli_system = {area: "" for area in ["requirement_management", "requirement_engineering", "system_engineering", "project_engineering"]}
        for area in dettagli_system.keys():
            if area not in scelte_progetti_system:  
                continue  
            tecnologie = request.form.getlist(f'tecnologie_{area}[]')
            ambito = request.form.getlist(f'azienda_{area}[]')
            durata = request.form.getlist(f'durata_{area}[]')
            descrizione = request.form.getlist(f'descrizione_{area}[]')
            #print(f"{area} -> Tecnologie: {tecnologie}, Ambito: {ambito}, Durata: {durata}, Descrizione: {descrizione}")
            esperienze = []
            for i in range(max(len(tecnologie), len(ambito), len(descrizione))):
                t = tecnologie[i] if i < len(tecnologie) else ""
                a = ambito[i] if i < len(ambito) else ""
                e = durata[i] if i < len(durata) else ""
                d = descrizione[i] if i < len(descrizione) else ""
                esperienze.append(f"{t} | {a} | {e} | {d}")
            dettagli_system[area] =esperienze
        #print(dettagli_system)
       

# Progetti Safety
        scelte_progetti_safety = request.form.getlist('safety')  
        dettagli_safety = {area: "" for area in ["RAMS", "hazard_analysis", "verification_report", "fire_safety", "reg_402"]}
        #print(request.form) 
        for area in dettagli_safety.keys():
            if area not in scelte_progetti_safety: 
                continue  

            tecnologie = request.form.getlist(f'tecnologie_{area}[]')
            ambito = request.form.getlist(f'azienda_{area}[]')
            durata = request.form.getlist(f'durata_{area}[]')
            descrizione = request.form.getlist(f'descrizione_{area}[]')
            #print(f"{area} -> Tecnologie: {tecnologie}, Ambito: {ambito}, Durata: {durata}, Descrizione: {descrizione}")
            esperienze = []
            for i in range(max(len(tecnologie), len(ambito), len(descrizione))):
                t = tecnologie[i] if i < len(tecnologie) else ""
                a = ambito[i] if i < len(ambito) else ""
                e = durata[i] if i < len(durata) else ""
                d = descrizione[i] if i < len(descrizione) else ""
                esperienze.append(f"{t} | {a} | {e} | {d}")
            dettagli_safety[area] =esperienze
        #print(dettagli_safety)
      

# Progetti Segnalamento      
        scelte_progetti_segnalamento = request.form.getlist('segnalamento')  
        dettagli_seg = {area: "" for area in ["piani_schematici_segnalamento", "cfg_impianti", "layout_apparecchiature", "architettura_rete", "computo_metrico"]}
        for area in dettagli_seg.keys():
            if area not in scelte_progetti_segnalamento:  
                continue  

            tecnologie = request.form.getlist(f'tecnologie_{area}[]')
            ambito = request.form.getlist(f'azienda_{area}[]')
            durata = request.form.getlist(f'durata_{area}[]')
            descrizione = request.form.getlist(f'descrizione_{area}[]')
            #print(f"{area} -> Tecnologie: {tecnologie}, Ambito: {ambito}, Durata: {durata}, Descrizione: {descrizione}")
            esperienze = []
            for i in range(max(len(tecnologie),len(ambito), len(descrizione))):
                t = tecnologie[i] if i < len(tecnologie) else ""
                a = ambito[i] if i < len(ambito) else ""
                e = durata[i] if i < len(durata) else ""
                d = descrizione[i] if i < len(descrizione) else ""
                esperienze.append(f"{t} | {a} | {e} | {d}")
            dettagli_seg[area] = esperienze
        #print(dettagli_seg)
       



# Progetti BIM
        progetti_bim_si_no = request.form.get('progetti_bim', 'No')  
        scelte_progetti_bim = request.form.getlist('bim')  
        #print(scelte_progetti_bim) 
        dettagli_bim = {area: "" for area in ["modellazione_e_digitalizzazione", "verifica_analisi_e_controllo_qualita", "gestione_coordinamento_e_simulazione", "visualizzazione_realtavirtuale_e_rendering"]}
        #print(request.form) 
        for area in dettagli_bim.keys():
            if area not in scelte_progetti_bim:  
                continue  
            tool = request.form.getlist(f'tool_{area}[]')
            azienda = request.form.getlist(f'azienda_{area}[]')
            durata = request.form.getlist(f'durata_{area}[]')
            descrizione = request.form.getlist(f'descrizione_{area}[]')
            certificazione = request.form.getlist(f'certificazioni_{area}[]')
            #print(f"{area} -> Tool: {tool}, Azienda: {azienda}, Durata: {durata}, Descrizione: {descrizione}, Certificazioni: {certificazione}")
            esperienze = []
            for i in range(max(len(certificazione), len(tool), len(azienda), len(descrizione))):
                t = tool[i] if i < len(tool) else ""
                a = azienda[i] if i < len(azienda) else ""
                e = durata[i] if i < len(durata) else ""
                d = descrizione[i] if i < len(descrizione) else ""
                c = certificazione[i] if i < len(certificazione) else ""
                esperienze.append(f" {t} | {a} | {e} | {d} | {c}")
            dettagli_bim[area] =esperienze
        #print("dettagli bim",dettagli_bim)
    


# Progetti PM
        progetti_pm_si_no = request.form.get('progetti_pm', 'No')  
        scelte_progetti_pm = request.form.getlist('pm')  
        dettagli_pm = {area: "" for area in ["project_manager_office", "project_manager", "risk_manager", "resource_manager", "quality_manager", "communication_manager", "portfolio_manager", "program_manager","team_leader", "business_analyst", "contract_back_office"]}
        #print(request.form) 
        for area in dettagli_pm.keys():
            if area not in scelte_progetti_pm:  
                continue  

            tool = request.form.getlist(f'tool_{area}[]')
            azienda = request.form.getlist(f'azienda_{area}[]')
            durata = request.form.getlist(f'durata_{area}[]')
            descrizione = request.form.getlist(f'descrizione_{area}[]')
            #print(f"{area} -> Tool: {tool}, Azienda: {azienda}, Durata: {durata}, Descrizione: {descrizione}")
            esperienze = []
            for i in range(max(len(tool), len(azienda), len(descrizione))):
                t = tool[i] if i < len(tool) else ""
                a = azienda[i] if i < len(azienda) else ""
                e = durata[i] if i < len(durata) else ""
                d = descrizione[i] if i < len(descrizione) else ""
                esperienze.append(f"{t} | {a} | {e} | {d}")
            dettagli_pm[area] =esperienze
        #print("dettagli pm",dettagli_pm)
       


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
            "Clienti Railway":  clienti_str, 
            "Area Railway": area_str, 
            "Normative": normative, 
            "Metodologie lavoro": metodologia_str,
            "Sistemi Operativi": sistemi_operativi,
            "Info aggiuntive": altro_str,
            "Hobby": hobby_str,
           # "Progetti Sviluppo": progetti_sviluppo_si_no,
           # "Aree progetti Sviluppo": ", ".join(scelte_progetti_sviluppo),
           # "Aree progetti V&V": ", ".join(scelte_progetti_vv),
           # "Aree progetti Safety": ", ".join(scelte_progetti_safety),
           # "Aree progetti System": ", ".join(scelte_progetti_system),
           # "Aree progetti Segnalamento": ", ".join(scelte_progetti_segnalamento),
           # "Progetti BIM": progetti_bim_si_no,
           # "Progetti PM": progetti_pm_si_no,

        }




        # Aggiunta delle varie sezioni con i dettagli in ordine
        aggiungi_sezione("Sviluppo", scelte_progetti_sviluppo, dettagli_sviluppo,data)
        aggiungi_sezione("V&V", scelte_progetti_vv, dettagli_vv,data)
        aggiungi_sezione("Safety", scelte_progetti_safety, dettagli_safety,data)
        aggiungi_sezione("System", scelte_progetti_system, dettagli_system,data)
        aggiungi_sezione("Segnalamento", scelte_progetti_segnalamento, dettagli_seg,data)

        aggiungi_sezione("BIM", scelte_progetti_bim, dettagli_bim,data)
        aggiungi_sezione("Project Management", scelte_progetti_pm, dettagli_pm,data)   



        #salvataggio dei ati nel file Excel
        if request.form['action'] == 'submit_main':
            df = pd.read_excel(EXCEL_FILE)
            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
            df.to_excel(EXCEL_FILE, index=False)

            success_message = "Risposta salvata con successo!"
            show_delete_button = True  # Mostra il pulsante per eliminare la risposta appena inviata


            ####################### salvataggio del file con le risposte del singolo utente ####################
            user_df = pd.DataFrame([data])
            user_df=user_df.drop(user_df.columns[0], axis=1)  #rimuove l'id

            user_filename = f"skills_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
            print("user_file_name",user_filename)
            user_filepath = os.path.join(USER_FILES_DIR, user_filename)
            print(user_filepath)
            # Salvataggio del file
            user_df.to_excel(user_filepath, index=False)

    
        elif request.form['action'] == 'delete_from_main' and user_id:
            print(user_id)
            # Elimina i dati dal file principale
            remove_user_from_main_file(user_id-1)
            success_message = "Risposta eliminata dal file principale!"
            show_delete_button = False  # Nascondi il pulsante di eliminazione dopo l'eliminazione

    return render_template("form.html", success_message=success_message, show_delete_button=show_delete_button,  user_filename=user_filename) 

@app.route("/download")
def download():
    file_type = request.args.get("file", "main")  # Valore di default: 'main'

    if file_type == "personal":
        filename = request.args.get("filename")  # Il nome del file personale
        if not filename:
            return abort(400, description="Missing filename parameter")
        
        user_filepath = os.path.join(USER_FILES_DIR, filename)
        if not os.path.exists(user_filepath):
            return abort(404, description="File not found")

        return send_file(user_filepath, as_attachment=True, download_name=filename)


    if not os.path.exists(EXCEL_FILE):
        return abort(404, description="File not found")

    return send_file(EXCEL_FILE, as_attachment=True, download_name="skills_trial.xlsx")


if __name__ == "__main__":
    app.run(debug=True)
