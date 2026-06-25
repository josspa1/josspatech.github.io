#!/usr/bin/env python3
"""Generate user-guide-pt or user-guide-it from user-guide-fr template."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FR = ROOT / "videos" / "user-guide-fr" / "index.html"

LOCALES = {
    "pt": {
        "lang": "pt-BR",
        "title": "Guia completo do usuário - PocketBudJet | JosspaTech",
        "nav_home": "Início",
        "nav_products": "Produtos",
        "nav_guides": "Guias",
        "nav_download": "Baixar",
        "breadcrumb_guide": "Guia do usuário",
        "hero_h1": "O guia completo do PocketBudJet",
        "hero_sub": "Cada tela. Cada função. Cada configuração. Um tour visual de tudo o que o PocketBudJet pode fazer pelas suas finanças — para comunidades lusófonas nos Estados Unidos.",
        "section_h2": "Assista ao tour completo",
        "section_sub": "Telas reais, pulso dourado onde tocar, narração passo a passo.",
        "tap_label": "Toque para reproduzir",
        "timeline_h2": "O tour completo — 28 capítulos",
        "cta_h2": "Pronto para retomar o controle das suas finanças?",
        "cta_p": "Baixe o PocketBudJet hoje e comece com o tour do guia completo integrado ao app.",
        "cta_btn": "Baixar",
        "footer_home": "Início",
        "footer_products": "Produtos",
        "slide_badge": "Slide {n} de 28",
        "voice_title": "Ativar/desativar narração",
        "voice_aria": "Ativar/desativar narração",
        "play_title": "Reproduzir/Pausar",
        "mp3_comment": "MP3 EN reutilizado até re-voice pt-BR (edge-tts)",
        "chapters": [
            "Primeiros passos", "Painel", "Transações", "Importar", "Digitalizar",
            "Orçamentos", "Contas", "Poupança", "Dívidas", "Investimentos",
            "Relatórios", "Coach IA", "Assistente IA", "Busca", "Exportar",
            "Painel PC", "Importar", "Família", "Calendário", "Regras",
            "Acessibilidade", "Mindful", "Aposentadoria", "Voz", "Preços",
            "Privacidade", "Dados", "Ajuda",
        ],
        "cards": [
            ("Bem-vindo e configuração", "Baixe o PocketBudJet, siga o assistente de configuração, crie sua primeira conta e inicie seu teste Premium de 21 dias — sem cartão. Depois do teste, assine mensal ou anualmente para manter o acesso. O assistente guia nome, moeda, contas, renda (bruta e líquida), contas a pagar, metas e estilo de orçamento — tudo que o app precisa para ser inteligente desde o primeiro dia."),
            ("Seu painel", "Cartões de renda, despesas e saldo no topo. O indicador de ritmo de gastos mostra se você está no caminho certo. Widgets de ações rápidas. Alertas de anomalias sinalizam transações incomuns. O indicador compara onde você está com onde deveria estar neste ponto do mês."),
            ("Adicionar transações", "Toque em +, digite o valor, escolha uma categoria — pronto. Divida transações em várias categorias. Anexe fotos de recibos. Use modelos para lançamentos recorrentes. Dica: escreva nomes de comerciantes sempre igual — «Daily Grind», não «DAILY GRIND» — para agrupar corretamente nos relatórios."),
            ("Importar dados", "Importe extratos CSV, OFX, QFX, QIF, XLSX ou PDF — sem login bancário. O Smart Mapper detecta colunas automaticamente. Detecção de duplicatas evita contagens em dobro. Importe pelo menos três meses de histórico — mais dados significam IA mais inteligente. Sincronização bancária automática (somente EUA, via Teller) é opcional com Premium pago — não durante o teste de 21 dias. Para instruções passo a passo, veja nosso <a href=\"/videos/import/\" style=\"color: #1A4F7A; font-weight: 600; text-decoration: underline;\">vídeo de importação de dados bancários</a>."),
            ("Digitalizar documentos", "Digitalize recibos com a câmera. OCR lê comerciante, valor e data. Suporte a scanner WiFi conecta seu scanner ADF doméstico para processamento em lote. Lê até caligrafia. Até onde sabemos, o PocketBudJet é o único app de orçamento com suporte a scanner WiFi."),
            ("Gerenciar orçamentos", "Cinco modelos de orçamento ou crie o seu. Limites por categoria com barras coloridas. Transfira orçamento não usado. Visão geral de saúde mostra sua posição. Relatórios de variação comparam planejado vs. real."),
            ("Contas e recorrentes", "Calendário visual de contas com datas de vencimento. Pontos verdes marcam dias de pagamento. Configure receitas e despesas recorrentes. Previsão inteligente estima contas futuras com base nos seus hábitos."),
            ("Poupança e metas", "Defina metas de poupança com datas-alvo. Crie fundos de reserva. Lista de desejos com reflexão de 30 dias para frear compras impulsivas. Calculadora «e se» mostra trade-offs. A janela de 30 dias é um lembrete — adicione algo que quer comprar e o PBJ espera 30 dias antes de contar."),
            ("Quitar dívidas", "Acompanhe todas as dívidas em um só lugar. Escolha avalanche (maior taxa primeiro) ou bola de neve (menor saldo primeiro). Veja sua data de liberdade financeira. Cenários «e se» mostram como pagamentos extras aceleram a quitação."),
            ("Investimentos e patrimônio", "Acompanhe ações, cripto (19 moedas) e valor imobiliário via estimativas Zillow. Monitore seu score de crédito. Veja apólices de seguro junto aos ativos para visão completa do patrimônio líquido."),
            ("Relatórios e análises", "Mais de 10 tipos de relatórios: gastos por categoria, receitas vs. despesas, comparações ano a ano, painel de anomalias, tendência de patrimônio e relatórios personalizados."),
            ("Coach financeiro IA", "Insights personalizados com base nos seus hámetros de gasto. Somente com opt-in. Detecta tendências, alerta sobre atividade incomum e envia resumo semanal. Quanto mais dados, mais inteligente fica."),
            ("Assistente IA", "Pergunte sobre seu dinheiro em linguagem natural. «Quanto gastei em restaurantes no mês passado?» ou «Estou acima do orçamento?» Onze tipos de consulta, tudo processado no seu dispositivo."),
            ("Encontrar qualquer função", "O PocketBudJet tem dezenas de funções — você não descobrirá todas navegando ao acaso. Busque transações por valor ou comerciante. Busque funções: tente «quilometragem», «voz», «aposentadoria» ou «daltonismo». Se perguntar se o PBJ faz algo, busque."),
            ("Exportar e compartilhar", "Exporte em seis formatos: CSV, XLSX, OFX, PDF, JSON e backup criptografado. Gere relatório pronto para contador. Inicie servidor LAN para transferir arquivos ao computador."),
            ("Painel Web PC", "Acesse o PocketBudJet de qualquer navegador na rede local. Escaneie QR para parear. Cinco abas: Painel, Transações, Orçamentos, Relatórios, Configurações. CRUD completo. Sincronização em tempo real com o telefone."),
            ("Flexibilidade de importação", "Importe de CSV, OFX, QIF e PDF — sem conexão bancária. Digitalize recibos com a câmera. Transfira recibos digitais do e-mail. Arraste arquivos no painel PC. Sincronização bancária (somente EUA) permanece opcional com Premium pago."),
            ("Sincronização familiar", "Sincronize com familiares via WiFi ou Bluetooth — sem internet. Pareie com QR. Orçamentos compartilhados com visibilidade individual. Resolução automática de conflitos."),
            ("Visão calendário", "Calendário mensal com pontos de transação a cada dia. Vencimentos e dias de pagamento. Codificado por categoria. Toque em qualquer dia para ver transações."),
            ("Favoritos e regras", "Marque transações importantes. Crie regras de categorização automática por comerciante. Edite várias transações em lote. Regras economizam tempo — defina «Daily Grind → Café» e cada transação futura se categoriza sozinha."),
            ("Acessibilidade", "Modo escuro, alto contraste e paletas para daltônicos. Bloqueio biométrico. Texto ampliado. Compatível com leitores de tela."),
            ("Funções mindful", "Visão mindful remove números e mostra anéis de progresso. Modo custo em tempo converte preços em horas de trabalho. Estrelas PBJ gamificam a poupança. Um jantar de US$ 50 vira «2,5 horas de trabalho»."),
            ("Planejamento de aposentadoria", "Acompanhe marcos de poupança Fidelity. Calculadora FIRE. Projeções de taxa de retirada segura. Estimador de renda na aposentadoria."),
            ("Atalhos de voz", "Funciona com Siri e Google Assistant. Seis atalhos integrados: adicionar transação, ver saldo, status do orçamento e mais. Crie atalhos personalizados."),
            ("Preços", "Comece com teste Premium de 21 dias — acesso completo, sem cartão. Sincronização bancária (somente EUA, via Teller) exige assinatura Premium paga — não durante o teste. Depois, assine mensal ou anual. Cancele quando quiser. Sem anúncios, sem venda de dados."),
            ("Privacidade e segurança", "Seus dados ficam no armazenamento privado do PocketBudJet no dispositivo. Nenhuma credencial bancária é armazenada. Backup e nuvem são opcionais — criptografia AES-256 com chave só sua. Sincronização bancária opcional (somente EUA) via Teller no Premium pago."),
            ("Dados e armazenamento", "Defina quanto tempo o backup guarda detalhes completos, quantos meses ficam no telefone para acesso offline e como imagens de recibos são distribuídas. Toque em Revisar e liberar espaço para pré-visualizar antes de agir. Resumos anuais são mantidos permanentemente."),
            ("Precisa de ajuda?", "Escreva para support@josspatech.com — respondemos em até 24 horas. Use o formulário de feedback no app. Visite <a href=\"/how-to/\" style=\"color: #1A4F7A; font-weight: 600; text-decoration: underline;\">josspatech.com/how-to</a> para guias em vídeo sobre importação, orçamento, dívidas, digitalização e mais."),
        ],
        "timeline": [
            ("Primeiros passos", "Download, assistente, teste 21 dias"),
            ("Painel", "Visão financeira de relance"),
            ("Transações", "Rastrear, buscar e categorizar cada dólar"),
            ("Importar", "CSV, OFX, QFX, QIF, XLSX, PDF — sem login bancário"),
            ("Digitalizar", "Câmera, scanner WiFi, OCR, caligrafia"),
            ("Orçamentos", "Modelos, limites, acompanhamento"),
            ("Contas", "Calendário visual e recorrentes"),
            ("Poupança", "Metas, reservas, lista de desejos"),
            ("Dívidas", "Bola de neve ou avalanche com data de liberdade"),
            ("Investimentos", "Ações, cripto, imóveis, score"),
            ("Relatórios", "Mais de 10 tipos e personalizados"),
            ("Coach IA", "Insights e resumos semanais"),
            ("Assistente IA", "Perguntas em linguagem natural"),
            ("Busca", "Transações e funções instantaneamente"),
            ("Exportar", "Seis formatos mais backup criptografado"),
            ("Painel PC", "Acesso via navegador na rede local"),
            ("Importar", "CSV, OFX, QIF, PDF, recibos"),
            ("Família", "Sync WiFi ou Bluetooth"),
            ("Calendário", "Visão mensal com pontos e vencimentos"),
            ("Regras", "Categorização automática e lote"),
            ("Acessibilidade", "Escuro, daltônico, leitor de tela"),
            ("Mindful", "Custo em tempo e bem-estar"),
            ("Aposentadoria", "FIRE e marcos"),
            ("Voz", "Siri e Google Assistant"),
            ("Preços", "Teste 21 dias; sync bancária EUA = Premium pago"),
            ("Privacidade", "Criptografia no dispositivo, nuvem opcional"),
            ("Dados", "Retenção, histórico local, recibos"),
            ("Ajuda", "E-mail e feedback no app"),
        ],
    },
    "it": {
        "lang": "it",
        "title": "Guida utente completa - PocketBudJet | JosspaTech",
        "nav_home": "Home",
        "nav_products": "Prodotti",
        "nav_guides": "Guide",
        "nav_download": "Scarica",
        "breadcrumb_guide": "Guida utente",
        "hero_h1": "La guida completa a PocketBudJet",
        "hero_sub": "Ogni schermata. Ogni funzione. Ogni impostazione. Un tour visivo di tutto ciò che PocketBudJet può fare per le tue finanze — per le comunità italiane negli Stati Uniti.",
        "section_h2": "Guarda il tour completo",
        "section_sub": "Schermate reali, impulso dorato dove toccare, narrazione passo passo.",
        "tap_label": "Tocca per riprodurre",
        "timeline_h2": "Il tour completo — 28 capitoli",
        "cta_h2": "Pronto a riprendere il controllo delle tue finanze?",
        "cta_p": "Scarica PocketBudJet oggi e inizia con il tour della guida completa integrata nell'app.",
        "cta_btn": "Scarica",
        "footer_home": "Home",
        "footer_products": "Prodotti",
        "slide_badge": "Slide {n} di 28",
        "voice_title": "Attiva/disattiva narrazione",
        "voice_aria": "Attiva/disattiva narrazione",
        "play_title": "Riproduci/Pausa",
        "mp3_comment": "MP3 EN riutilizzato fino a re-voice it-IT (edge-tts)",
        "chapters": [
            "Primi passi", "Dashboard", "Transazioni", "Importa", "Scansione",
            "Budget", "Bollette", "Risparmio", "Debiti", "Investimenti",
            "Report", "Coach IA", "Assistente IA", "Cerca", "Esporta",
            "Dashboard PC", "Importa", "Famiglia", "Calendario", "Regole",
            "Accessibilità", "Mindful", "Pensione", "Voce", "Prezzi",
            "Privacy", "Dati", "Aiuto",
        ],
        "cards": [
            ("Benvenuto e configurazione", "Scarica PocketBudJet, segui la procedura guidata, crea il tuo primo conto e avvia la prova Premium di 21 giorni — senza carta. Dopo la prova, abbonati mensile o annuale per mantenere l'accesso. La procedura guidata copre nome, valuta, conti, reddito (lordo e netto), bollette, obiettivi e stile di budget."),
            ("La tua dashboard", "Schede reddito, spese e saldo in alto. L'indicatore del ritmo di spesa mostra se sei in linea. Widget per azioni rapide. Avvisi di anomalia segnalano transazioni insolite."),
            ("Aggiungere transazioni", "Tocca +, inserisci l'importo, scegli una categoria — fatto. Dividi transazioni su più categorie. Allega foto di scontrini. Usa modelli per voci ricorrenti. Suggerimento: scrivi i nomi dei commercianti sempre allo stesso modo per raggrupparli correttamente nei report."),
            ("Importare dati", "Importa estratti CSV, OFX, QFX, QIF, XLSX o PDF — nessun login bancario. Smart Mapper rileva le colonne. Rilevamento duplicati evita conteggi doppi. Importa almeno tre mesi di storico. Sincronizzazione bancaria automatica (solo USA, via Teller) è opzionale con Premium a pagamento — non durante la prova di 21 giorni. Vedi il nostro <a href=\"/videos/import/\" style=\"color: #1A4F7A; font-weight: 600; text-decoration: underline;\">video sull'importazione dati bancari</a>."),
            ("Scansionare documenti", "Scansiona scontrini con la fotocamera. OCR legge commerciante, importo e data. Supporto scanner WiFi per elaborazione batch. Legge anche la scrittura a mano. PocketBudJet è l'unica app di budget con supporto scanner WiFi che conosciamo."),
            ("Gestire i budget", "Cinque modelli di budget o crea il tuo. Limiti per categoria con barre colorate. Trasferisci budget non usato. Panoramica salute mostra la tua posizione."),
            ("Bollette e ricorrenti", "Calendario visivo delle bollette con scadenze. Punti verdi segnano i giorni di paga. Configura entrate e uscite ricorrenti. Previsione intelligente stima le bollette future."),
            ("Risparmio e obiettivi", "Imposta obiettivi di risparmio con date target. Crea fondi di riserva. Lista desideri con riflessione di 30 giorni. Calcolatore «e se» mostra i compromessi."),
            ("Eliminare i debiti", "Traccia tutti i debiti in un unico posto. Scegli avalancha (tasso più alto) o palla di neve (saldo minore). Vedi la data di libertà dal debito. Scenari «e se» mostrano come pagamenti extra accelerano il rimborso."),
            ("Investimenti e patrimonio netto", "Traccia azioni, crypto (19 valute) e valore immobiliare via stime Zillow. Monitora il punteggio di credito. Visualizza polizze assicurative accanto agli asset."),
            ("Report e analisi", "Oltre 10 tipi di report: spese per categoria, entrate vs. uscite, confronti anno su anno, dashboard anomalie, trend patrimonio netto e report personalizzati."),
            ("Coach finanziario IA", "Insight personalizzati basati sulle tue abitudini di spesa. Solo con opt-in. Rileva tendenze, avvisa attività insolite e invia riepilogo settimanale."),
            ("Assistente IA", "Fai domande sul tuo denaro in linguaggio naturale. «Quanto ho speso al ristorante il mese scorso?» Undici tipi di query, tutto elaborato sul dispositivo."),
            ("Trovare qualsiasi funzione", "PocketBudJet ha decine di funzioni. Cerca transazioni per importo o commerciante. Cerca funzioni: prova «chilometraggio», «voce», «pensione» o «daltonismo»."),
            ("Esporta e condividi", "Esporta in sei formati: CSV, XLSX, OFX, PDF, JSON e backup crittografato. Genera report pronto per il commercialista. Avvia server LAN per trasferire file al computer."),
            ("Dashboard Web PC", "Accedi a PocketBudJet da qualsiasi browser sulla rete locale. Scansiona QR per accoppiare. Cinque schede: Dashboard, Transazioni, Budget, Report, Impostazioni. CRUD completo. Sincronizzazione in tempo reale con il telefono."),
            ("Flessibilità di importazione", "Importa da CSV, OFX, QIF e PDF — senza connessione bancaria. Scansiona scontrini cartacei. Trasferisci ricevute digitali dall'email. Trascina file nella dashboard PC. Sync bancaria (solo USA) opzionale con Premium a pagamento."),
            ("Sincronizzazione familiare", "Sincronizza con familiari via WiFi o Bluetooth — senza internet. Accoppia con QR. Budget condivisi con visibilità individuale. Risoluzione automatica conflitti."),
            ("Vista calendario", "Calendario mensile con punti transazione ogni giorno. Scadenze bollette e giorni di paga. Codificato per categoria. Tocca un giorno per vedere le transazioni."),
            ("Preferiti e regole", "Segna transazioni importanti. Crea regole di categorizzazione automatica per commerciante. Modifica più transazioni in batch."),
            ("Accessibilità", "Modalità scura, alto contrasto e palette per daltonici. Blocco biometrico. Testo ingrandito. Compatibile con screen reader."),
            ("Funzioni mindful", "Vista mindful rimuove i numeri e mostra anelli di progresso. Modalità costo in tempo converte i prezzi in ore di lavoro. Una cena da 50 $ diventa «2,5 ore di lavoro»."),
            ("Pianificazione pensione", "Traccia traguardi risparmio Fidelity. Calcolatore FIRE. Proiezioni tasso di prelievo sicuro. Stimatore reddito pensionistico."),
            ("Scorciatoie vocali", "Funziona con Siri e Google Assistant. Sei scorciatoie integrate. Crea scorciatoie vocali personalizzate."),
            ("Prezzi", "Inizia con prova Premium di 21 giorni — accesso completo, senza carta. Sincronizzazione bancaria (solo USA, via Teller) richiede abbonamento Premium a pagamento — non durante la prova. Poi abbonati mensile o annuale. Cancella quando vuoi. Niente pubblicità, niente vendita dati."),
            ("Privacy e sicurezza", "I tuoi dati restano nello storage privato di PocketBudJet sul dispositivo. Nessuna credenziale bancaria memorizzata. Backup e cloud opzionali — crittografia AES-256 con chiave solo tua. Sync bancaria opzionale (solo USA) via Teller su Premium a pagamento."),
            ("Gestione dati e storage", "Definisci quanto tempo il backup conserva i dettagli completi, quanti mesi restano sul telefono per accesso offline e come le immagini degli scontrini sono distribuite. Tocca Rivedi e libera spazio per anteprima prima di agire."),
            ("Serve aiuto?", "Scrivi a support@josspatech.com — rispondiamo entro 24 ore. Usa il modulo feedback nell'app. Visita <a href=\"/how-to/\" style=\"color: #1A4F7A; font-weight: 600; text-decoration: underline;\">josspatech.com/how-to</a> per guide video su importazione, budget, debiti, scansione e altro."),
        ],
        "timeline": [
            ("Primi passi", "Download, procedura guidata, prova 21 giorni"),
            ("Dashboard", "Panoramica finanziaria"),
            ("Transazioni", "Traccia, cerca e categorizza ogni dollaro"),
            ("Importa", "CSV, OFX, QFX, QIF, XLSX, PDF — senza login bancario"),
            ("Scansione", "Fotocamera, scanner WiFi, OCR"),
            ("Budget", "Modelli, limiti, monitoraggio"),
            ("Bollette", "Calendario visivo e ricorrenti"),
            ("Risparmio", "Obiettivi, riserve, lista desideri"),
            ("Debiti", "Palla di neve o avalancha con data libertà"),
            ("Investimenti", "Azioni, crypto, immobili, credit score"),
            ("Report", "Oltre 10 tipi e personalizzati"),
            ("Coach IA", "Insight e riepiloghi settimanali"),
            ("Assistente IA", "Domande in linguaggio naturale"),
            ("Cerca", "Transazioni e funzioni istantaneamente"),
            ("Esporta", "Sei formati più backup crittografato"),
            ("Dashboard PC", "Accesso browser in rete locale"),
            ("Importa", "CSV, OFX, QIF, PDF, scontrini"),
            ("Famiglia", "Sync WiFi o Bluetooth"),
            ("Calendario", "Vista mensile con punti e scadenze"),
            ("Regole", "Categorizzazione automatica e batch"),
            ("Accessibilità", "Scuro, daltonico, screen reader"),
            ("Mindful", "Costo in tempo e benessere"),
            ("Pensione", "FIRE e traguardi"),
            ("Voce", "Siri e Google Assistant"),
            ("Prezzi", "Prova 21 giorni; sync bancaria USA = Premium a pagamento"),
            ("Privacy", "Crittografia on-device, cloud opzionale"),
            ("Dati", "Conservazione, storico locale, scontrini"),
            ("Aiuto", "Email e feedback in-app"),
        ],
    },
}


def build(locale: str) -> str:
    cfg = LOCALES[locale]
    html = FR.read_text(encoding="utf-8")

    html = html.replace('lang="fr"', f'lang="{cfg["lang"]}"')
    html = html.replace(
        "Guide utilisateur complet - PocketBudJet | JosspaTech",
        cfg["title"],
    )
    html = html.replace(">Accueil</a>", f">{cfg['nav_home']}</a>")
    html = html.replace(">Produits</a>", f">{cfg['nav_products']}</a>")
    html = html.replace(">Guides</a>", f">{cfg['nav_guides']}</a>")
    html = html.replace(">Télécharger</a>", f">{cfg['nav_download']}</a>")
    html = html.replace(">Guide utilisateur</span>", f">{cfg['breadcrumb_guide']}</span>")
    html = html.replace(
        "Le guide complet PocketBudJet",
        cfg["hero_h1"],
    )
    html = html.replace(
        "Chaque écran. Chaque fonction. Chaque réglage. Une visite visuelle de tout ce que PocketBudJet peut faire pour vos finances — pour les communautés francophones aux États-Unis.",
        cfg["hero_sub"],
    )
    html = html.replace("Regardez la visite complète", cfg["section_h2"])
    html = html.replace(
        "Écrans réels, impulsion dorée là où appuyer, narration pas à pas.",
        cfg["section_sub"],
    )
    html = html.replace("Appuyez pour lire", cfg["tap_label"])
    html = html.replace("La visite complète — 28 chapitres", cfg["timeline_h2"])
    html = html.replace(
        "Prêt à reprendre le contrôle de vos finances ?",
        cfg["cta_h2"],
    )
    html = html.replace(
        "Téléchargez PocketBudJet dès aujourd'hui et commencez avec la visite du guide utilisateur complet intégrée à l'application.",
        cfg["cta_p"],
    )
    html = html.replace('class="download-button">Télécharger</a>', f'class="download-button">{cfg["cta_btn"]}</a>')
    html = html.replace("MP3 audio: EN narration reused until FR re-voice", cfg["mp3_comment"])
    html = html.replace('title="Lecture/Pause"', f'title="{cfg["play_title"]}"')
    html = html.replace('title="Activer/désactiver la narration vocale"', f'title="{cfg["voice_title"]}"')
    html = html.replace(
        'aria-label="Activer/désactiver la narration vocale"',
        f'aria-label="{cfg["voice_aria"]}"',
    )

    # Replace narration cards (match FR order)
    fr_cards = [
        ("Diapositive 1 sur 28", "Bienvenue et configuration"),
        ("Diapositive 2 sur 28", "Votre tableau de bord"),
        ("Diapositive 3 sur 28", "Ajouter des transactions"),
        ("Diapositive 4 sur 28", "Importer des données"),
        ("Diapositive 5 sur 28", "Numériser des documents"),
        ("Diapositive 6 sur 28", "Gérer les budgets"),
        ("Diapositive 7 sur 28", "Factures et transactions récurrentes"),
        ("Diapositive 8 sur 28", "Épargne et objectifs"),
        ("Diapositive 9 sur 28", "Réduire les dettes"),
        ("Diapositive 10 sur 28", "Investissements et patrimoine net"),
        ("Diapositive 11 sur 28", "Rapports et analyses"),
        ("Diapositive 12 sur 28", "Coach financier IA"),
        ("Diapositive 13 sur 28", "Assistant IA"),
        ("Diapositive 14 sur 28", "Trouver n'importe quelle fonction instantanément"),
        ("Diapositive 15 sur 28", "Export et partage"),
        ("Diapositive 16 sur 28", "Tableau de bord Web PC"),
        ("Diapositive 17 sur 28", "Flexibilité d'import"),
        ("Diapositive 18 sur 28", "Synchronisation familiale"),
        ("Diapositive 19 sur 28", "Vue calendrier"),
        ("Diapositive 20 sur 28", "Favoris et règles"),
        ("Diapositive 21 sur 28", "Accessibilité"),
        ("Diapositive 22 sur 28", "Fonctions de pleine conscience"),
        ("Diapositive 23 sur 28", "Planification de la retraite"),
        ("Diapositive 24 sur 28", "Raccourcis vocaux"),
        ("Diapositive 25 sur 28", "Tarifs"),
        ("Diapositive 26 sur 28", "Confidentialité et sécurité"),
        ("Diapositive 27 sur 28", "Gestion des données et du stockage"),
        ("Diapositive 28 sur 28", "Besoin d'aide ?"),
    ]

    for i, ((fr_badge, fr_h3), (h3, body)) in enumerate(
        zip(fr_cards, cfg["cards"])
    ):
        n = i + 1
        badge = cfg["slide_badge"].format(n=n)
        html = html.replace(f"<span class=\"narration-step-badge\">{fr_badge}</span>", f"<span class=\"narration-step-badge\">{badge}</span>", 1)
        html = html.replace(f"<h3>{fr_h3}</h3>", f"<h3>{h3}</h3>", 1)
        # Replace paragraph in narration card - find after h3
        import re
        pattern = rf"(<h3>{re.escape(h3)}</h3>\s*<p>)(.*?)(</p>)"
        html = re.sub(pattern, rf"\1{body}\3", html, count=1, flags=re.DOTALL)

    fr_chapters = [
        "Premiers pas", "Tableau de bord", "Transactions", "Import", "Numérisation",
        "Budgets", "Factures", "Épargne", "Dettes", "Investissements",
        "Rapports", "Coach IA", "Assistant IA", "Recherche", "Export",
        "Tableau PC", "Import", "Famille", "Calendrier", "Règles",
        "Accessibilité", "Mindful", "Retraite", "Voix", "Tarifs",
        "Confidentialité", "Données", "Aide",
    ]
    for fr_btn, loc_btn in zip(fr_chapters, cfg["chapters"]):
        html = html.replace(f'>{fr_btn}</button>', f'>{loc_btn}</button>', 1)

    fr_timeline = [
        ("Premiers pas", "Téléchargement, assistant, essai 21 jours"),
        ("Tableau de bord", "Votre aperçu financier en un coup d'œil"),
        ("Transactions", "Suivre, rechercher et catégoriser chaque dollar"),
        ("Import", "Relevés CSV, OFX, QFX, QIF, XLSX, PDF — sans connexion bancaire"),
        ("Numérisation", "Appareil photo, scanner WiFi, OCR, écriture manuscrite"),
        ("Budgets", "Modèles, limites personnalisées, suivi de progression"),
        ("Factures", "Calendrier visuel et transactions récurrentes"),
        ("Épargne", "Objectifs, fonds de réserve, liste de souhaits, calculateur"),
        ("Dettes", "Boule de neige ou avalanche avec date de libération"),
        ("Investissements", "Actions, crypto, immobilier, score de crédit"),
        ("Rapports", "Plus de 10 types de rapports et rapports personnalisés"),
        ("Coach IA", "Analyses personnalisées et récapitulatifs hebdomadaires"),
        ("Assistant IA", "Posez des questions en langage courant"),
        ("Recherche", "Trouvez transactions et fonctions instantanément"),
        ("Export", "Six formats plus sauvegarde chiffrée"),
        ("Tableau PC", "Accès navigateur sur le réseau local"),
        ("Import", "CSV, OFX, QIF, PDF, reçus photo, reçus électroniques"),
        ("Famille", "Synchronisation WiFi ou Bluetooth en famille"),
        ("Calendrier", "Vue mensuelle avec points de transaction et échéances"),
        ("Règles", "Catégorisation automatique et modification en lot"),
        ("Accessibilité", "Mode sombre, palettes daltoniennes, lecteur d'écran"),
        ("Mindful", "Mode coût en temps et bilans bien-être"),
        ("Retraite", "Calculateur FIRE et suivi des jalons"),
        ("Voix", "Raccourcis Siri et Google Assistant"),
        ("Tarifs", "Essai 21 jours, puis mensuel ou annuel ; sync bancaire US = Premium payant"),
        ("Confidentialité", "Chiffrement sur l'appareil, cloud facultatif"),
        ("Données", "Rétention des sauvegardes, historique local, reçus"),
        ("Aide", "Support par courriel et commentaires intégrés"),
    ]
    for (fr_h, fr_p), (loc_h, loc_p) in zip(fr_timeline, cfg["timeline"]):
        html = html.replace(f"<h3>{fr_h}</h3>", f"<h3>{loc_h}</h3>", 1)
        # timeline p tags - be careful with duplicates
        block = f"<h3>{loc_h}</h3>\n <p>{fr_p}</p>"
        new_block = f"<h3>{loc_h}</h3>\n <p>{loc_p}</p>"
        if block in html:
            html = html.replace(block, new_block, 1)

    return html


def main():
    locale = sys.argv[1] if len(sys.argv) > 1 else "pt"
    out_dir = ROOT / "videos" / f"user-guide-{locale}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "index.html"
    out_path.write_text(build(locale), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
