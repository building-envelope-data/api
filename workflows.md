Which workflows should be considered to add corresponding endpoints to metabase?

Kontext erste Angestellte einer Institution registriert sich
Angestellte1 legt Benutzerkonto1 an, bestehend aus E-Mail-Adresse und Passwort.
Falls Benuterkonto1 nicht über den Link in der Mail bestätigt wird, wird es nach 2 Monaten gelöscht.
Falls Angestellte1 ihr Passwort vergessen haben sollte, muss sie das Passwort zurücksetzen können über die E-Mail-Adresse.
Gib mir alle Daten über diese Person inklusive aller Interaktionen, die diese Person verursacht hat.
Lösche alle Daten über diese Person.
Deaktivierung von Benutzerkonten. Danach taucht das Benutzerkonto in öffentlichen Suchen nicht mehr auf.
Aktivierung von Benutzerkonten.
E-Mail-Adresse ändern
Passwort ändern
Profil ändern
Sekundäre E-Mail-Adresse angebbar
Sekundäre zur primären E-Mail-Adresse machen
DSGVO-Rückfrage vor dem Löschen des Benutzerkontos
Angestellte1 markiert Metadaten ihres Benutzerkontos als öffentlich.
Angestellte1 markiert Metadaten ihres Benutzerkontos als privat.

Kontext Verifikation Person oder Institution
Angestellte3 arbeitet fürs Fraunhofer ISE und ist Verifikationsverantwortliche.
Angestellte3 kann die Verifikationsverantwortung mit anderen Benutzern wie Angestellte4 teilen.
Angestellte3 kann Verifikationsverantwortung abgeben, wenn es andere Verifikationsverantwortliche gibt
Angesteller3 erteilt Verifikationsberechtigung an Angestellte5.
Angestellte5 kann durch die Verifikationsberechtigung Institutionen und Benutzer mit “verifiziert” markieren, z.B. wenn eine Institution einen rechtsverbindlichen Auftrag zur Aufnahme in die Metabase erteilt hat.
Angesteller3 entzieht Verifikationsberechtigung von Angestellter5.

Kontext Datenbank wird registriert
Institution2 besitzt die DB2.
Hauptverantwortliche1 der Institution2 registriert die DB2 in der Metabase und erhält einen Code, der in der Metainformation der Domäne oder als Datei hinzufügen, um die Datenbank zu verifizieren.
Hauptverantwortliche1 bestätigt, dass die Verifikationsdaten in der DB2 hinterlegt sind. Diese werden geprüft. Wenn vorhanden, wird DB2 für die nächsten 6 Monate als verifiziert markiert, sonst nur Fehlermeldung.
DB2 fragt einmal pro Monat bei der Metabase nach dem neuen Code und implementiert den.
DB2 schickt eine Verlängerungsanfrage an die Metabase. Wenn der Code stimmt, wird die Verifikation um 6 Monate verlängert.
Fehler DB2 URL stimmt nicht.
Fehler API-Spezifikation der DB2 stimmt nicht. Prüfen der API-Minimalanforderungen gemäß DB-GraphQL

Kontext InstitutionRepresentatives
Erste Angestellte einer Institition1 registriert diese und wird dadurch Hauptverantwortliche1 (InstitutionRepresentative).
Hauptverantwortliche1 fügt andere Benutzerkonten der Institution1 hinzu.
Hauptverantwortliche1 entfernt Benutzerkonten von der Institution1.
Hauptverantwortliche1 kann Hauptverantwortung mit anderen Benutzern teilen.
Hauptverantwortliche1 kann Hauptverantwortung abgeben, wenn es andere Hauptverantwortliche gibt.

Kontext Standardisierungsorganisationen
ISE gibt Angestellter6 github-Verantwortung.
Institution7 schlägt eine zusätzliche Standardisierungsorganisation vor und liefert deren Metadaten.
Angestellte6 übernimmt den Vorschlag/Pull Request und erweitert damit die API-Spezifikation.
Angestellte6 trägt die Metadaten entweder selbst ein oder beauftragt Angestellte1.
ISE gibt Angestellter1 die Berechtigung, Infos über Standardisierungsorganisationen zu erstellen, zu ändern und als aufgelöst zu markieren.
ISE entzieht Angestellter1 die Berechtigung, Infos über Standardisierungsorganisationen zu erstellen, zu ändern und als aufgelöst zu markieren.

Kontext Rechte der Hauptverantwortlichen einer Institution
Hauptverantwortliche1 von Institution1 erteilt Angestellter2 die Berechtigung2.
Angestellte2 mit Berechtigung2

- erstellt Komponenten, Komponentenversionen, Methoden, dataFormats, Benutzerkonten für Mitarbeitende von Institution1, Assoziationen wie ComponentManufacturer, MethodDeveloper
- ändert Metadaten von Komponenten, Komponentenversionen, Methoden, dataFormats, Benutzerkonten für Mitarbeitende von Institution1, Assoziationen wie ComponentManufacturer, MethodDeveloper
- markiert Komponenten, Komponentenversionen, Methoden, dataFormats, Benutzerkonten für Mitarbeitende von Institution1, Assoziationen wie ComponentManufacturer, MethodDeveloper als “aufgelöst”.

Kontext dataFormats
Angestellte3 arbeitet fürs Fraunhofer ISE, ist dataFormat-Verantwortliche und hat damit automatisch auch eine dataFormat-Berechtigung.
Angestellte3 kann die dataFormat-Verantwortung mit anderen Benutzern wie Angestellte4 teilen.
Angestellte3 kann dataFormat-Verantwortung abgeben, wenn es andere dataFormat-Verantwortliche gibt.
Angestellte3 kann dataFormats, die von keinem data set genutzt werden, löschen.
Angestellte5 fragt nach allen dataFormat-Berechtigten und erhält die E-Mail-Adressen.
Angestelle3 erteilt dataFormat-Berechtigung an Angestellte5.
Angestellte5 kann durch die dataFormat-Berechtigung neue dataFormats erstellen und diese ändern.
Angesteller3 entzieht dataFormat-Berechtigung von Angestellter5.

Kontext einer bereits registrierten Institution registriert sich (Affiliation)
Angestellte2 der bereits registrierten Institution1 registriert sich und wird informiert über die Namen der Hauptverantwortlichen und bittet diese um Aufnahme in Institution1.
Hauptverantwortliche1 nimmt Angestellte2 in die Institution auf und gib ihr die nötigen Rechte.
Hauptverantwortliche1 entzieht Angestellter2 bestimmte Rechte.
Hauptverantwortliche1 entfernt Angestellte2 aus der Institution und entzieht ihr alle Rechte.
Angestellte2 ändert die Metadaten ihres Benutzerkontos.

Kontext Vollmacht für Institutionen
Hauptverantwortliche1 von Institution1 erteilt Institution2 eine Generalvollmacht.
Hauptverantwortliche2 nimmt für Institution2 die Vollmacht an.
Hauptverantwortliche1 von Institution1 entzieht Institution2 eine Generalvollmacht.
Hauptverantwortliche1 von Institution1 erteilt Institution2 eine Vollmacht für die Komponenten1-10 und deren Versionen.
Hauptverantwortliche2 nimmt für Institution2 die Vollmacht an.
Hauptverantwortliche1 von Institution1 entzieht Institution2 die Vollmacht für Komponente1 und deren Versionen.
Hauptverantwortliche1 lässt sich alle Änderungen anzeigen, die mit einer Vollmacht in einem bestimmten Zeitraum durchgeführt wurden.
Hauptverantwortliche2 teilt eine Vollmacht mit Angestellter3.
Hauptverantwortliche2 entzieht Angestellter3 eine Vollmacht.

Kontext gemeinsame Komponenten
Institution1 legt Komponente1 an und wird dadurch Hersteller der Komponente.
Institution2 stellt Komponente1 ebenfalls her. Institution1 beantragt, dass Institution2 ebenfalls Hersteller der Komponente zu wird. Institution2 bestätigt dies oder lehnt es ab.
Institution2 stellt Komponente1 ebenfalls her und beantragt, ebenfalls Hersteller der Komponente zu sein. Institution1 bestätigt dies oder lehnt es ab.

Kontext Reflexive Beziehungen im allgemeinen
Institution1 bittet Institution2 um Bestätigung der reflexiven Beziehung zwischen ihren Komponenten.

Kontext Associations
Institution8 becomes a member of Association1.
Institution9 submits data to Regional-Data-Aggregator1 (RDA1) of Association1.
RDA1 informs Association1 that with Institution9, a new institution is registered.
Currently, no direct access between Association1 and RDA1 to the data about institutions. The cases in which it is needed are rare.
RDA1 processes the submission and informs Association1 about which work has been done. 
Association1 sends an invoice to Institution9.
If Institution9 does not pay the invoice, its data is deleted.
Association1 reviews the peer review of RDA1.
