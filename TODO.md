# TODOs unified-ui

## Plan

*Erst Foundry, und Langchain anbinden, bevor wir Tracings umsetzen, damit wir tracing-logiken aus verschiedenen 

- Foundry anbinden
    - Simplen Agent bauen
        - Agent
        - Multi-Agent (Workflow)
            - Send Message
            - Ask a question
    - platform-service
        - bei POST /conversation -> wenn Foundry -> hier auch foundry conversation anlegen und in db speichern (in config feld der conversation -> kann dann über /config zurückgegeben werden!)
    - Integration in GO mit sdk bauen
    - Integration testen (postman)
    - Config im Frontend implementieren
    - Agent im Frontend testen
```txt
Notizen foundry:
- conversation hat automantisch an conversation die chat history dran -> wir brauchen keine history mitgeben, nur auf conversation beziehen!
- 
```

- Copilot anbinden
    - python sdk -> FastAPI Copilot Chat service
        - trigger über agent-service
        - FastAPI nur für Copilot-Anbindung -> alles sonst in GO agent-service
    - Integration in GO mit sdk bauen
    - Integration testen (postman)
    - Config im Frontend implementieren
    - Agent im Frontend testen

- Langchain und Langgraph REST API Service
    - einen simplen Langchain Agent bauen -> per REST API exposen
    - state auch irgendwie senden
        - einfach als dict?
    - Integration in GO mit sdk bauen
    - Integration testen (postman)
    - Config im Frontend implementieren
    - Agent im Frontend testen

- Tracing implementieren
    - Collection entwickeln
    - N8N anbinden
    - Frontend tracing im Chat einbauen
        - klick auf message -> Rechte Sidebar für tracing einbauen und anzeigen

- Frontend
    - Credentials raus aus Sidebar und in Tenant-Settings rein
        - extra Tab; ähnlich wie Cutsom Groups
    - ConversationPage schöner designen
    - bugs beheben
        - systematisch jede Seite durchgehen und checken
            - wenn was hinzugefügt wird, wird jeder State aktualisiert?
        - beim wechseln des tenants
            - context leeren
                - zB sidebardatalist sind noch die bereits gefetcheten sachen dabei
        
        - beim fetchen der Credentials im Create- und EditApplicationDialog wird noch credentials?limit=999 gefetcht -> hier eher paginierung, aber man kann ruhig 100 fetchen (nur name und id -> + orderBy=name order_direction=asc)
        - siehe Video vom 02.01.
    - ConversationPage
        - Search implementieren
    - weitere features
        - PIN (favorietes)
    - Dashboard
    - ...

- Agent-Service
    - GET secret endpoint hinzufügen
        - GET /api/v1/platform-service/tenants/{id}/credentials/{id}/secret
    - autonomous agents
        - hier API Key generieren lassen, inkl. rotate
            - beim erstellen: werden in VAULT gespeichert und referenz uri in db auf autonomous-agent
            - PUT /api/v1/platform-service/tenants/{id}/autonomous-agents/{id}/keys/1|2/rotate
                - werden 
    - traces implementieren
        - beim messages senden -> in jobQueue nach ende die traces fetchen und speichern (N8N -> traces collection)
            - traces mit message id ODER autonomous-agent-id speichern 
        - POST endpoint mit selben service implementieren

11. ZWEI Vaults fixen:
    - app_vault + secrets_vault
        - App Vault für application keys wie zB `X-Service-Key`
        - Secrets Vault -> ist vault für credentials aus der app etc...
    - *aktuell in auth.py > _validate_service_key soll app_vault nutzen
        - app_vault kann auch dotenv sein...

- models.py refactoren
    - überall wo uuid von uns -> char(36) nutzen
        - zb bei Conversation.application_id string(100) -> char(36)

- Bei delete conversation -> auch messages und traces löschen

- Frontend-Tests entwickeln

## Future

- Backend
    - Agent-Integration
        - reasoning?...

- Frontend
    - /refresh von identity implementieren
        - FE button in IAM table -> da wo das icon ganz links ist -> beim hovern hier ein refresh icon rein!

    - Rollen im FE beachten
        - GLOBAL_ADMIN, *CREATOR, *ADMIN
        - TENANT manages acces etc etc

    - language-support einbauen
        - erstmal alles in englisch
        - als zweites: über url /de-de /en-us übersetzen (default -> /en-us)
