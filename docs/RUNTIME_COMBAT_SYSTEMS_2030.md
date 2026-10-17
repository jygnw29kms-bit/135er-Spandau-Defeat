# Spandau Strike – Runtime Combat Systems 2030

## Zweck
Diese Spezifikation übersetzt die festgelegte Spielidentität in konkrete Laufzeitregeln für UE5/Lyra. Ziel bleibt: taktisch, direkt, hohe Letalität, schnelle Rückkehr ins Gefecht, keine Squad-Abhängigkeit und kein Milsim-Verwaltungsballast.

## Respawn
Respawns laufen als Team-Wellen entlang der aktuellen Front. Die Basiswelle beträgt 10 Sekunden, gleichzeitig gilt eine minimale Todeszeit von 4 Sekunden. Spawnpunkte werden serverseitig aus sicheren Frontbändern gewählt. Direkte Feindsicht, geringe Gegnerdistanz und kürzlich stark belastete Spawnpunkte werden vermieden. Nach Sektorwechsel rückt die Spawnlinie nach der festgelegten 20-Sekunden-Übergangsphase vor.

Ziel bleibt 15 bis 35 Sekunden vom Spawn bis zu sinnvoller Gefechtsbeteiligung. Lange Laufwege sind kein Gameplayziel.

## HUD
Das HUD bleibt minimal und kontextbezogen. Dauerhaft sichtbar sind nur relevanter Objective-Zustand und Tickets, wenn der Modus sie benötigt. Munition, Haltung, Interaktionen, Friendly-ID und Capture-Fortschritt erscheinen nur dann deutlich, wenn sie gebraucht werden.

Nicht zulässig sind Schadenszahlen, dauerhaft schwebende Feindmarker, permanente Feind-Outlines und Killstreak-Banner-Spam. Gegner sollen durch Welt, Bewegung, Silhouette, Audio und Beobachtung erkannt werden, nicht durch Leuchtreklame.

## Punktewertung
Objectives schlagen K/D. Richtwerte:
- Kill 100
- Assist 50
- Defense Kill 150
- vollständige Capture-Beteiligung 250
- Capture-Ticks 5
- Smoke Support 20
- Resupply 15
- Recon Assist 35

Die Werte sind Balancing-Baselines und werden später per Playtest justiert. Das Verhältnis ist wichtiger als die exakte Zahl: Frontarbeit und Teamnutzen müssen sichtbar belohnt werden.

## Munition und Versorgung
Munition ist endlich. Kein automatisches Nachfüllen während eines Lebens. Support-Versorgung hat 45 Sekunden Cooldown. Granaten werden nur begrenzt nachgefüllt und haben 90 Sekunden Nachfüll-Cooldown, damit aus Capture kein permanenter Explosivhagel wird. Derselbe Versorgungspunkt darf pro Leben nur begrenzt genutzt werden.

## Suppression
Suppression erzeugt Druck, nimmt aber nicht die Kontrolle weg. Nahe Geschossvorbeiflüge, Schussknall und Einschläge erzeugen Audio-Stress und leichte Zielunruhe. Keine künstliche Blindheit, keine Eingabesperre, kein erzwungenes Waffensenken.

Die technische Basis arbeitet mit Near-Miss-Radius, kurzem Akkumulationsfenster und schneller Erholung. Damit bleibt Feuerunterstützung taktisch relevant, ohne den Spieler mit Effekten zu bestrafen, gegen die er nichts tun kann.

## Sprache und Kommunikation
Teamkanal und Proximity-Voice sind vorgesehen, kein Squadkanal. Proximity-Voice fällt über etwa 35 Meter ab. Kontext-Pings haben Cooldown und Burst-Limit gegen Spam.

135er-Funk bleibt Deutsch mit natürlichem Berliner/Spandauer Einschlag. Die Gegenseite funkt überwiegend Englisch, strukturierter und technischer.

## Rundenfluss
30 Sekunden Warmup, danach laufende Front. Sektorwechsel nutzen 20 Sekunden Übergang. Overtime läuft nur, solange ein relevanter Punkt umkämpft ist oder aktiver Capture-Fortschritt besteht. Nach Matchende folgen 20 Sekunden Ergebnisphase.

## Inspirationsfilter
Von Day of Defeat übernehmen wir Direktheit, Klassenlesbarkeit und kurze Rückkehr ins Gefecht. Von Insurgency die Bedeutung von Audio, Munition, Rauch und reduzierter HUD-Abhängigkeit. Von Rising Storm die 64-Spieler-Intensität, asymmetrische Fraktionsidentität und lokale Kommunikation. Von Breakthrough-artigen Modi übernehmen wir nur den Frontfluss. Nicht übernommen werden Squad-Zwang, Commander-Abhängigkeit, FOB-Schleifen oder kilometerlange Anmärsche.
