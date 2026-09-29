# MoneyMindz /wallstreet-bot via GitHub

Typ `/wallstreet` in de Telegram-groep. De bot antwoordt met precies drie regels:
de stand van de S&P 500, Dow Jones en Nasdaq Composite. Iedere regel toont de
tijd van de koers in Nederlandse tijd. Buiten beursuren is dit de laatste
beschikbare stand; het zijn geen futures of premarketprijzen.

## Installeren vanaf je telefoon

1. Maak via [@BotFather](https://t.me/BotFather) een **nieuwe bot** met `/newbot`.
   Voeg die bot toe aan je Telegram-groep. Gebruik niet de token van je bestaande
   premarketbot: twee taken met `getUpdates` op dezelfde bot kunnen elkaar hinderen.
2. Maak op GitHub een **public repository** voor deze twee bestanden. Hierin komt
   geen token; dat bewaar je als secret. Upload `wallstreet.py` in de hoofdmap.
3. Maak het tweede bestand aan met exact dit pad:
   `.github/workflows/wallstreet.yml` (inclusief de punt vóór `github`).
   Plak daarin de YAML-code uit het pakket. Sla beide bestanden op in de
   standaardbranch (`main`). GitHub detecteert dan de workflow onder **Actions**.
4. Open **Settings → Secrets and variables → Actions → Repository secrets →
   New repository secret**. Naam `TELEGRAM_BOT_TOKEN`; waarde: de token van de
   nieuwe bot uit BotFather. Zet deze token nooit in code of in de groep.
5. Typ `/wallstreet` in de groep. Open voor de eerste test **Actions →
   MoneyMindz Wall Street commando → Run workflow**. Wacht op de groene check;
   de bot hoort nu in dezelfde groep drie regels te plaatsen. Daarna kijkt
   GitHub zelf op geplande momenten naar nieuwe commando's.

Je hoeft geen groeps-ID op te zoeken. `/wallstreet@JouwBotNaam` werkt ook.
Als het commando in de groep niet wordt ontvangen, maak de bot beheerder of
stuur het commando expliciet met `@JouwBotNaam` erachter.

## Verwachting en grenzen

GitHub Actions controleert elke vijf minuten en start niet gegarandeerd exact
op tijd. Een antwoord duurt dus gewoonlijk enkele minuten en kan bij vertraging
of een overgeslagen geplande run langer duren. Gebruik een server/webhook als
een onmiddellijk antwoord noodzakelijk is. De workflow draait dag en nacht.

Voor een *public* repository zijn standaard GitHub Actions-minuten gratis;
in een *private* repository telt iedere geplande run mee voor de maandelijkse
limiet. De code gebruikt geen groeps-ID of opgeslagen berichten. Hij leest
alleen recente Telegram-updates van deze eigen bot en bevestigt ze na
verwerking. Telegram bewaart onbevestigde updates niet onbeperkt.

De koersbron is het onofficiële Yahoo Finance chart-endpoint. Dat kan vertraagd
zijn, tijdelijk weigeren of veranderen. Bij een fout antwoordt de bot met een
foutmelding in plaats van een verzonnen stand. Voor gegarandeerde realtime
data en herpublicatierechten is een gelicentieerde koersfeed nodig.
