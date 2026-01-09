
- Konzept für Tracing Visualisierung
    - Daten:
        - Root
            - ReferenceName
            - ContextType
            - ReferenceId
            - Logs
            - ReferenceMetadata -> einfach als JSON anzeigen
            - CreatedAt
        - Nodes
            - Name
            - Type
            - Status
            - RefrenceId
            - StartAt
            - Data
                - input
                    - Text
                    - ExtraData -> als Tab und JSON anzeigen
                    - Metadata -> als Tab und JSON anzeigen
                - output
                    - Text
                    - ExtraData -> als Tab und JSON anzeigen
                    - Metadata -> als Tab und JSON anzeigen
            - Logs
    - Einsatzgebiete
        1. im Chat
            - Anzeige der Hierarchischen Traces in einer Sidebar
                - Oben eine hierarchische View (primär Type im container und Name)
            - Für detaiierte View -> kann man Dialog mit Details öffnen
                - rechts auch die hierarchische view (horizontal größer kleiner ziehen)
                - links:
                    - oben Canvas workflow view mit items die connectet sind
                    - unten (kleiner, vertkakl größer kleiner ziehen)
        2. Autonomous Agent page -> detaiierte view im Dialog
    - Konzept:
        - wir bauen modular ein tracings-visualisierungs-interface
        - Es wird zwei Hauptkomponenten geben:
            - [Canvas-View] Ein Canvas, mit Visuellen Items, welche connected sind und einen Workflowartige Visualisierung darstellt
            - [Hierachie-View] Eine vertikale, hierarchischaufgebaute struktur, die primär text hierarchisch anzeigt und beim klicken informationen in einem unteren fenster anzeigt
        - Skizze der Gesamt Page:
            - Header:
                - Icon + "Tracing for referenceName" + contextType (drunter) schön anzeigen
                - und schließen icon, klar
            - Einen Subheader, der aber fixed ist und nur über dem convas liegt
                - hier gewissen daten anzeigen:
                    - trace_id
                    - SelectedItem name (oder root)
                    - SelectedItem startAt, endAt oder root startat etc (wenn nicht gegeben nicht anzeigen)
                    - status
            - Links (3/4 breit):
                - Canvas View (oben, initial 2/3 hoch):
                    - Items (nodes aus den daten)
                        - eher quadratisch mit runden ecken
                        - erstes item: ecken oben links und unten links mehr rundung
                        - letztes item: ecken oben rechts und unten rechts mehr rundung
                        - Im Center ein Icon
                            - du bekommst daten -> anhand der typen kannst du passende icons auswählen
                            - ein schönes default icon auswählen
                        - unter dem icon den name
                        - wenn success (oder synonym wie compleated etc (du bekommst noch daten dazu))
                            - border schönes grün
                            - ein hakchen unten rechts
                        - wenn selected -> shadow hinzufügen
                    - item connections
                        - mit pfeil verbunden (wie zB in N8N Workflows)
                        ### Canvas Layout Architecture (using xyflow/react)

                        #### Node Types
                        1. **Root Nodes**: Main execution steps, arranged in primary flow direction
                        2. **Sub-Nodes**: Nested execution details, branching off from parent nodes

                        #### Layout Strategy
                        - **Primary Flow**: Horizontal (left-to-right) or vertical (top-to-bottom), user-toggleable
                        - **Sub-Node Branching**: Always perpendicular to primary flow
                            - Horizontal mode: sub-nodes branch downward
                            - Vertical mode: sub-nodes branch rightward

                        #### Edge Connection Pattern
                        ```
                        ┌──────────┐    ┌──────────┐    ┌──────────┐
                        │  Node 1  │───▶│  Node 2  │───▶│  Node 3  │   ← Primary flow
                        └──────────┘    └──────────┘    └──────────┘
                                                                 │
                                                                 ├──[1]──▶ SubNode A
                                                                 │              │
                                                                 │              └──[1]──▶ SubSubNode X
                                                                 │
                                                                 └──[2]──▶ SubNode B
                        ```

                        #### Sub-Node Branching Rules
                        1. **Branch Origin**: Edges exit from the bottom (horizontal) or right (vertical) of parent node
                        2. **Index Labels**: Each branch edge displays a small numbered badge (1, 2, 3...) at the branch point
                        3. **Spacing Calculation**: 
                             - Fixed vertical/horizontal gap between sibling sub-nodes
                             - Parent node reserves space based on total descendant count (recursive)
                        4. **Curved Edges**: Use smooth bezier curves for branch edges (xyflow `smoothstep` or `bezier` edge type)

                        #### Collapse/Expand Behavior
                        - **Toggle Button**: Circular icon button centered on the branch edge
                            - Collapsed: `+` icon, edge hidden, sub-tree hidden
                            - Expanded: `−` icon, edge visible, sub-tree visible
                        - **State Propagation**: Collapsing a node hides all descendants; expanding reveals immediate children only
                        - **Layout Recalculation**: Use xyflow's `fitView()` or custom layout algorithm to smoothly reposition nodes after toggle

                        #### Implementation Notes
                        - Use xyflow's `useNodesState` and `useEdgesState` for reactive updates
                        - Custom node component with status indicator (border color + icon)
                        - Custom edge component with collapse/expand button
                        - Calculate node positions using recursive depth-first traversal, accumulating offsets based on subtree sizes
                - Data Section (unten, initial ca 1/3 hoch)
                    - höhenanpassbar
                    - Links: Logs anzeigen
                        - Headertitel: Logs (root)
                        - Wenn kein Item selektiert -> root-logs anzeigen
                        - Wenn Item selektiert -> node-logs anzeigen
                        - eher schmal (inital 1/4 breit)
                    - rechts:
                        - initial 3/4 breit
                        - Header
                            - Tab-Bar
                                - Input + Output (nicht bei root)
                                - Metadata (referenceMetadata bei root)
                        - Input + Output:
                            - 1/2 und 1/2, breitenanpassbar
                            - Input:
                                - Text oben
                                - metadata (als JSON view)
                                - extraData (als JSON view)
                                - alle drei sections ein und ausblendbar
                                    - initial nur Text eingeblendet und anderen zu
                            - Output: wie input
                    - links/rechts breitenanpassbar
            - rechts (1/4 breit; breite anpassbar)
                - Oben: Hierarchy-View
                    - Hierachie view der Items, wie bei foundry (siehe bild)
                    - diese dient ebenfalls für die navigation und selektierung von items
                        - wenn conversation mehrere traces hat -> hier default ist die erste ausgewählt (über context kann man auch id angeben)
                        - man kann aber auch dann eine untere auswählen, dann werden die items der conversation im canvas gerendert, aus der selected conversation (*bei autonom agent wird immer nur ein trace ausgewäht!)
                    - zur hierarchie:
                        - root item ist trace oder wenn mehrere traces gegeben (nur bei conversations kann dies der fall sein, aber auch nicht wichtig), werden diese untereinander gerendert
                        - man kann root und jedes sub item entsprechend collapsen und expanden (defautl alles expandedt)
                        - item:
                            - root:
                                - Im Badge: contextType, daneben referenceName, daneben kleines icon für status
                            - node (gilt ebenso für subnodes)
                                - Im Badge: Node.type, danmeben name, daneben kleines icon für status (wenn null oder unbekannt -> einfach weglassen)
                            - wenn der name zu lang ist, wird dieser einfach abgeschnitten mit "..."
                                - beim selektieren, wird im sub header ja der name eh angezeigt
                        - die hierarchie zwischen root, nodes und subnodes wird immer mit einem schönem bogen gekennzeichnet und entsprechend der hierarchie gibt es dann links beim bogen etwas padding (beim ersten nur das icon, dann padding etc; siehe foto foundry)
                    - wenn man ein item in der hierarchie anklickt, wird dieses selektiert und dies sieht man dann auch ind er canvas view (shadow)
                        - zudem soll die canvas view dann zu diesem item im canvas navigieren und diesen zentriert zeigen
                - Unten:
                    - erstmal nur ein leerer container mit 30px höhe (placeholer)
                    - ist aber höhenverstellbar
        - Canvas
            - Canvas soll
                - mit Maus navigierbar sein (also linke maustaste gedrück halten und dann mit maus verschieben)
                - vergrößer und verkleinerbar sein (mit STRG Scroll oder wie auf Mac mit trackpad einfach rein und rausscrollen)
                - mit zB Mac Trackpad auch verschiebar (also einfach auch mit wischen mit zwei fingern schön im canvas navigieren -> du weißt bescheid)
                - man kann einzelne items auch margieren mit der Maus -> dann sieht man daten dazu, hier ist aber nur wichtig, dass halt dann um das item die border und viduell hervorgehoben wird (nur shadow?)
                - so typische buttons:
                    - zum start navigeren und "zentrieren"
                    - vergrößern
                    - verkleinern
                    - view: horizental, vertikal -> wie die items angeordnet werden (default horizontal!)

Für die Entwicklung der traces-visualisierung, bauen mir bitte die page `TracingDialogDevelopment`, welche unter `/dev/tracing` aufrufbar ist.
Default soll der Dialog direkt aufgehen und über query params will ich steuern, welche traces du holst:
entweder:
    - ?conversationId={"CONVERSATION_ID"} => dann fetchst du `{{host_agent_service}}/api/v1/agent-service/tenants/{{tenant_id}}/conversations/{{conversation_id}}/traces`
        - returns : {"traces": [...]}
        - siehe api client; wenn noch nicht implementiert, schaue in die routes.go und response schema und implementiere den client.ts und types.ts für diese route
    - ?autonomousAgentId={"AUTO_AGENT_ID"} => dann fetchst du `{{host_agent_service}}/api/v1/agent-service/tenants/{{tenant_id}}/autonomous-agents/{{autonomous_agent_id}}/traces`
        - returns : {"traces": [...]}
        - siehe api client; wenn noch nicht implementiert, schaue in die routes.go und response schema und implementiere den client.ts und types.ts für diese route
        - => ja, hier bekommst du dann mehrere von auto agent traces, aber auch das sollte ja kein problem sien, da selbe response!

**Diene Aufgaben**
1. Analysiere meine Anforderungen und definiere für dich optimierte Anfordeurngen, mit denen du super arbeiten kannst
2. Analysiere die tracing struktur (siehe, wie N8N und foundry traces entsprechend importiert werden)
3. Analyisere die "unifiedui.traces.json" datei, um verschiedene Daten zu sehen, die du bekommen kannst
4. Analysiere die Projektstruktur des Frontend-services; insbesondere die design farben
5. Baue mir die Page `TracingDialogDevelopment` und erstelle im route die route `/dev/tracing`
6. Plane die Implementierung des `TracingVisualDialog` entsprechend modular (ich will im chat auch in einer quick view zB nur die hierarchie verwenden etc)
7. Implementiere die module für den `TracingVisualDialog` und letztendlich den dialog, der auch direkt aufgehen soll auf /dev/tracing?...

Sollten noch weitere UI Libraries nötig sein, gerne diskutiere mit dir, welche am besten passen würde.
