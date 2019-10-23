# K8ProjectManager
Kubernetes Project Manager zum erstellen, patchen und löschen von Kubernetes Projekten in kleinen bis mittleren localen Systemen mit vereinfachter Configuration

Sorry ... hab die Anleitung noch nicht geschrieben ... mach ich die nächsten Tage/Wochen

bis dahin:
- mit -p bekommt ihr die möglichen Config Optionen (das "s" an ende einer Section nicht mitschreiben, alle Sektionen sind in singular 
  außer "[claims]" das aber nur ein Keyword-Section ist falls zu allen Volumes jeweils ein Claim erstellt werden soll). 
- "scalirbar" heist man kann mehrere Sectoren und/oder Optionen in die config schreiben.
  z.B. [volume1] [volume2] oder unter [ingress] rule1_host= rule2_host=
- Die Sprachen müssen nicht vollständig übersetzt werden. Fehlende Übersetzungen weden durch die alternativ Sprache ersetzt.
- "von Vorgabe" läst zu das man Optionen von anderen Sectoren mit @ zuweist. 
  z.B. in Section [service] port3=@container2 wird den in [container2] definirten Port zum [service] auf option port3 eintragen
- Das Fehler Abfang System hat sich selbständig zu einen Art einfachen Assistens System gebildet. Heist, wenn man einen Service
  Deployen will mit einen Ingress Zugang macht man einfach eine Config in der nur [deploy] und [ingress] steht und das Programm 
  wird einen Stück für Stück sagen welche Sectoren und Optionen noch fehlen.
- Es läuft auch ohne Kubernetes aber erstelt dann nur die json Konfig für die Kubernetes Objecte

Für Programierer:
Richtlinien:
- Keine doppelten Config Informationen. Wenn 2 mal die selbe Information in die config geschriben werden müssen muss das Modul das selber aus der anderen Angabe in der Section oder Option übernehmen können.
- Das Config Object wird von Kubernetes Object Modul zu Kubernetes Object Modul erweitert bis es ein kompletes lückenloses Config Object ist.
- Die Config Optionen sind in den Modulen definirt. Erstes Flack sagt ob es Optional und 2. Flack sagt ob es Scalirbar ist. In 3. Feld steht was für ein Type die Config Option ist.
- Zentrale Verwaltung der Module ist die k8projectmanager_module.py. Sie legt fest welche Module existiren. In welcher Reihenfolge die Kubernetes Objecte generirt und gelöscht werden. Welche Kubernetes Methoden dabei benutzt werden.
- in sub_language.py ist die Text Liste für die Sprachen. Der Sprachcode wird durch getdefaultlocale ermittelt. Es kann auch eine Datei language.cfg mit der Text Liste als Config-File angelegt werden.
