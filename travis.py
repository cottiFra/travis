import sys
from travis_core import TravisCore

def main():
    core = TravisCore()
    print("Travis CLI: avvio dei modelli...")
    core.init_models(status_callback=lambda s: print(f"  {s}"))
    
    print("\nTravis è online.")
    core.parla("Sistema avviato. Dimmi Travis per attivarmi.")
    
    try:
        while True:
            core.aspetta_wake_word(on_detect_callback=lambda: print("Wake word 'Travis' rilevata!"))
            core.parla("Dimmi pure.")
            
            comando = core.ascolta_con_silenzio(status_callback=lambda s: print(f"[{s}]"))
            if not comando:
                print("Nessun comando rilevato.")
                continue
                
            print(f"Tu: {comando}")
            
            if "spegniti" in comando.lower() or "esci" in comando.lower():
                core.parla("Arrivederci.")
                break
                
            risultato_spotify = core.gestisci_spotify(comando)
            if risultato_spotify:
                core.parla(risultato_spotify)
                continue
                
            core.parla("Elaboro...")
            risposta = core.chiedi_ai(comando)
            codice = core.pulisci_codice(risposta)
            
            print(f"\nTravis esegue:\n{codice}\n")
            
            try:
                core.esegui_codice_sicuro(codice)
                core.parla("Fatto.")
            except Exception as e:
                core.parla(f"Errore: {e}")
                print(f"Errore durante l'esecuzione del codice: {e}")
                
    except KeyboardInterrupt:
        print("\nInterruzione da tastiera. Uscita...")
        core.parla("Arrivederci.")

if __name__ == "__main__":
    main()