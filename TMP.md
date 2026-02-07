Wir werden nun die Details page für Autonomous Agent page designen.

Für dich zur erläuerung:
autonomous agents sind quasi automatisierungsworkflows, welche extern laufen. wir bieten ihnen eine api, wo sie ihre traces (also was haben sie im wf gemacht) hinschicken können (wir können auch gewisse selbst importieren) und hier in einem unified ui anzeigen lassen.

wir haben eine tracing component gebaut, welche die traces entsprechend visualisiert. schaue dir dieses component gerne mal an. wird auf /dev/tracing entwickelt und ist soweit erstmal fertig.

so stelle ich. mir die detail page vor:

wir navigieren von der auto agent liste (klick) auf /autonomous-agents/{id}
oben soll dann der name des auto agents, ggf die description, type (aktuell nur N8N (upper)) und son paar tags anzezeigt werden auf dem page header (nicht app header) angezeigt werden.
Dann muss ich endpoint details und traces anzeigen können.
endpoint details sind:
- endpoint: POST {aktueller-host}/api/v1/agent-service/tenants/{tenant_id}/traces) (und copy)
- primary key (nicht visible, nur sterne mit toggle UND rotate button (wie in Azure zB)) darunter
- secondary key (nicht visible, nur sterne mit toggle UND rotate button) darunter
- keys soll man auch kopieren können, beim draufklicken mit entsprechender benachritigung

dann muss man eine liste an traces sehen.
spalten:
referenceId
referenceName
type (also Conversation, Auto. Agent)
contextType
createdAt
updatedAt
darüber noch nen filter:
- Filter
        - nach Tag, Monat, Jahr
- Sort by: create at, updated at (serverseitig)

baue diese tabelle auch ganz wichtig als component


ich bin mir nicht sicher, was das beste layout / design für diese page wäre
...
ne tabbar mit im ersten die traces, im zweiten details zum endpoint
    - sodass man erst die wichtigen infos sieht (die tracing liste -> infinity scroll, wie überall sonst auch)
oder oben diese endpoint daten und unten die tracing liste...
weiß nicht.

 du aber im agent service den autonomous agent endpoint zum auflisten der traces eines auto agents entsprechend noch anpassen und paginierung, sortierung unf filtermöglickeiten implementieren


Deine Aufgaben:
1. Analysiere die Anforderungen und definiere für dich optimale Anfordeunrgen
2. Analysiere die Fontend und die backendstrukturen (agents-service) um zu verstehen
3. Plane das Konzept für die Frontendpage (details page autonomous agent)
4. Plane deine implementierung
5. stelle mir dein konzept und implementierungsplan vor; stelle ggf. rückfragen
---

1. ja gerne. bei list nur die wichtigen daten holen; beim öffnen des dialogs dann auf konkrete /{id} fetchen und dann alles von dem tracing holen! Wichtig, danke!; mach aber gerne noch bei list einen query param: expand=true/false (default false) hin, dann kann man optional noch alles fetchen beim listen
2. Ja simple present ist super
3. Bitte zeige ein "Stift" Icon (also edit icon) bei den Daten (Name, ect) an. Da soll dann der Edit Dialog wie auch auf der autonomous agents page (listenseite) aufgehen und 1:1 so verwendet werden. sollte ne component sein und reusable sein ohne duplicate code, oder?
4. Du brauchst Manage access nicht, da (wie in 3. beschreiben) der edit dialog schon details UND manage access bearbeitet lässt.
aber ja: traces und endpoints in dieser reihenfolge
5. Wir werden diese Tabelle später noch zentral verwenden (daher auch als component). status feld finde ich super! aber ja, lass weg
-> da fällt mir noch ein: kannst du noch nen status-filter reinhauen (serverseitig?) das wäre geil -> aber gib mir erstmal feedback dazu
6. ja, lass weg
7. anders: du machst (wie schon beschreiben) expand qp rein. expand default false -> keine logs und keine nodes werden gefetcht, nur root data (du weißt schon) und bei expand=true alles.