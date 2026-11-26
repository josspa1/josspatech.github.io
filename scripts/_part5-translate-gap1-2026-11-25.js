/**
 * Part 5 — translate Gap 1 "Also in the app" blocks + one-find line on HHH/CVC locales.
 * Machine translation approved; brand/feature names protected.
 */
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const LANGS = ['es', 'zh', 'de', 'fr', 'pt', 'it', 'hi'];

const ONE_FIND = {
  es: 'Un buen hallazgo — la pieza que todos los demás pasaron de largo — y ya se pagó sola.',
  zh: '一次好发现——别人都走过的那件——就回本了。',
  de: 'Ein guter Fund — das Stück, an dem alle anderen vorbeiliefen — und es hat sich bezahlt gemacht.',
  fr: 'Une bonne trouvaille — la pièce que tout le monde a laissée — et elle s’est remboursée.',
  pt: 'Um bom achado — a peça que todos os outros passaram — e já se pagou.',
  it: 'Un buon ritrovo — il pezzo che tutti gli altri hanno lasciato — e si è ripagato.',
  hi: 'एक अच्छी खोज — वह चीज़ जिसे बाकी सब छोड़ गए — और ख़र्च निकल आया।',
};

const H2 = {
  es: 'También en la app',
  zh: '应用里还有',
  de: 'Auch in der App',
  fr: 'Aussi dans l’app',
  pt: 'Também na app',
  it: 'Anche nell’app',
  hi: 'ऐप में और भी',
};

const BLOCKS = {
  pbj: {
    es: `<h2>También en la app</h2>
    <ul>
      <li><strong>Hogar / parejas</strong> — comparte un presupuesto con tu pareja en el teléfono.</li>
      <li><strong>Patrimonio neto</strong> — activos y deudas en un solo sitio en Inicio.</li>
      <li><strong>Centro de impuestos y kilometraje</strong> — exportación fiscal y seguimiento de millas desde Inicio y Toolbox.</li>
      <li><strong>Atajos de voz y widgets</strong> — añadido rápido y widgets en la pantalla de inicio.</li>
      <li><strong>Informes de empresas</strong> — lee filings recientes desde Toolbox.</li>
      <li><strong>Captura de notificaciones (Android)</strong> — atrapa avisos de gasto de otras apps.</li>
      <li><strong>Categorías y reglas de movimientos</strong> — define cómo se agrupa y ordena el dinero.</li>
      <li><strong>Logros y comparación con pares</strong> — metas visibles en Progress y Coach.</li>
      <li><strong>Jubilación, seguros e inversiones</strong> — planificadores en la pestaña Progress.</li>
      <li><strong>Huella de carbono</strong> — estima a partir del gasto en Toolbox.</li>
      <li><strong>Escaneo de documentos</strong> — captura papeles en la app.</li>
      <li><strong>Lista de deseos de compra</strong> — guarda lo que quieres desde Activity.</li>
    </ul>`,
    zh: `<h2>应用里还有</h2>
    <ul>
      <li><strong>家庭 / 情侣</strong> — 在手机上与伴侣共享预算。</li>
      <li><strong>净资产</strong> — 在首页查看资产与负债。</li>
      <li><strong>税务中心与里程</strong> — 从首页和工具箱导出税务并跟踪里程。</li>
      <li><strong>语音快捷方式与小组件</strong> — 快速添加与主屏幕小组件。</li>
      <li><strong>公司 filings</strong> — 在工具箱阅读近期公司 filings。</li>
      <li><strong>通知捕获（Android）</strong> — 捕获其他应用的支出提醒。</li>
      <li><strong>分类与交易规则</strong> — 设定资金如何分组与自动归类。</li>
      <li><strong>成就与同伴对照</strong> — 在 Progress 与 Coach 可见目标。</li>
      <li><strong>退休、保险与投资</strong> — Progress 标签中的规划工具。</li>
      <li><strong>碳足迹</strong> — 根据支出在工具箱估算。</li>
      <li><strong>文档扫描</strong> — 把文件扫进应用。</li>
      <li><strong>购物心愿单</strong> — 在 Activity 保存想买的东西。</li>
    </ul>`,
    de: `<h2>Auch in der App</h2>
    <ul>
      <li><strong>Haushalt / Paare</strong> — teile ein Budget mit deinem Partner auf dem Handy.</li>
      <li><strong>Nettovermögen</strong> — Vermögen und Schulden an einem Ort auf Home.</li>
      <li><strong>Steuercenter &amp; Kilometer</strong> — Steuerexport und Meilen von Home und Toolbox.</li>
      <li><strong>Sprachkürzel &amp; Widgets</strong> — Schnelleingabe und Startbildschirm-Widgets.</li>
      <li><strong>Unternehmens-Filings</strong> — aktuelle Filings in der Toolbox lesen.</li>
      <li><strong>Benachrichtigungs-Erfassung (Android)</strong> — Ausgabenhinweise anderer Apps einfangen.</li>
      <li><strong>Kategorien &amp; Transaktionsregeln</strong> — wie Geld gruppiert und sortiert wird.</li>
      <li><strong>Erfolge &amp; Peer-Vergleich</strong> — sichtbare Ziele in Progress und Coach.</li>
      <li><strong>Ruhestand, Versicherung &amp; Anlagen</strong> — Planer im Progress-Tab.</li>
      <li><strong>CO₂-Fußabdruck</strong> — Schätzung aus Ausgaben in der Toolbox.</li>
      <li><strong>Dokumentenscan</strong> — Unterlagen in die App bringen.</li>
      <li><strong>Einkaufswunschliste</strong> — Wünsche aus dem Activity-Hub speichern.</li>
    </ul>`,
    fr: `<h2>Aussi dans l’app</h2>
    <ul>
      <li><strong>Foyer / couples</strong> — partagez un budget avec votre partenaire sur le téléphone.</li>
      <li><strong>Patrimoine net</strong> — actifs et dettes au même endroit sur Accueil.</li>
      <li><strong>Centre fiscal &amp; kilométrage</strong> — export fiscal et suivi des miles depuis Accueil et Toolbox.</li>
      <li><strong>Raccourcis vocaux &amp; widgets</strong> — ajout rapide et widgets d’écran d’accueil.</li>
      <li><strong>Filings d’entreprises</strong> — lisez les filings récents dans Toolbox.</li>
      <li><strong>Capture de notifications (Android)</strong> — attrapez les alertes de dépense d’autres apps.</li>
      <li><strong>Catégories &amp; règles de transactions</strong> — définissez comment l’argent est groupé.</li>
      <li><strong>Succès &amp; repère entre pairs</strong> — objectifs visibles dans Progress et Coach.</li>
      <li><strong>Retraite, assurance &amp; investissements</strong> — planificateurs dans l’onglet Progress.</li>
      <li><strong>Empreinte carbone</strong> — estimez à partir des dépenses dans Toolbox.</li>
      <li><strong>Scan de documents</strong> — capturez des papiers dans l’app.</li>
      <li><strong>Liste d’envies d’achat</strong> — enregistrez des souhaits depuis Activity.</li>
    </ul>`,
    pt: `<h2>Também na app</h2>
    <ul>
      <li><strong>Agregado / casais</strong> — partilhe um orçamento com o parceiro no telemóvel.</li>
      <li><strong>Património líquido</strong> — ativos e dívidas num só sítio no Início.</li>
      <li><strong>Centro fiscal e quilometragem</strong> — exportação fiscal e milhas a partir do Início e Toolbox.</li>
      <li><strong>Atalhos de voz e widgets</strong> — adição rápida e widgets no ecrã inicial.</li>
      <li><strong>Filings de empresas</strong> — leia filings recentes no Toolbox.</li>
      <li><strong>Captura de notificações (Android)</strong> — apanhe alertas de gasto de outras apps.</li>
      <li><strong>Categorias e regras de movimentos</strong> — defina como o dinheiro é agrupado.</li>
      <li><strong>Conquistas e comparação entre pares</strong> — metas visíveis em Progress e Coach.</li>
      <li><strong>Reforma, seguros e investimentos</strong> — planeadores no separador Progress.</li>
      <li><strong>Pegada de carbono</strong> — estime a partir dos gastos no Toolbox.</li>
      <li><strong>Digitalização de documentos</strong> — capture papéis na app.</li>
      <li><strong>Lista de desejos de compra</strong> — guarde desejos no hub Activity.</li>
    </ul>`,
    it: `<h2>Anche nell’app</h2>
    <ul>
      <li><strong>Nucleo / coppie</strong> — condividi un budget con il partner sul telefono.</li>
      <li><strong>Patrimonio netto</strong> — attività e debiti in un solo posto su Home.</li>
      <li><strong>Centro tasse e chilometraggio</strong> — export fiscale e miglia da Home e Toolbox.</li>
      <li><strong>Scorciatoie vocali e widget</strong> — aggiunta rapida e widget sulla home.</li>
      <li><strong>Filings aziendali</strong> — leggi i filings recenti dal Toolbox.</li>
      <li><strong>Cattura notifiche (Android)</strong> — intercetta avvisi di spesa di altre app.</li>
      <li><strong>Categorie e regole sulle transazioni</strong> — come raggruppare e ordinare i soldi.</li>
      <li><strong>Traguardi e confronto tra pari</strong> — obiettivi visibili in Progress e Coach.</li>
      <li><strong>Pensione, assicurazioni e investimenti</strong> — pianificatori nella scheda Progress.</li>
      <li><strong>Impronta di carbonio</strong> — stima dalla spesa nel Toolbox.</li>
      <li><strong>Scansione documenti</strong> — porta i documenti nell’app.</li>
      <li><strong>Lista desideri acquisti</strong> — salva i desideri dall’hub Activity.</li>
    </ul>`,
    hi: `<h2>ऐप में और भी</h2>
    <ul>
      <li><strong>परिवार / कपल</strong> — फ़ोन पर साथी के साथ बजट साझा करें।</li>
      <li><strong>नेट वर्थ</strong> — होम पर संपत्ति और कर्ज़ एक जगह।</li>
      <li><strong>टैक्स सेंटर और माइलेज</strong> — होम और Toolbox से टैक्स निर्यात और माइलेज।</li>
      <li><strong>वॉयस शॉर्टकट और विजेट</strong> — तेज़ जोड़ और होम-स्क्रीन विजेट।</li>
      <li><strong>कंपनी filings</strong> — Toolbox से हाल की कंपनी filings पढ़ें।</li>
      <li><strong>नोटिफ़िकेशन कैप्चर (Android)</strong> — अन्य ऐप्स के खर्च अलर्ट पकड़ें।</li>
      <li><strong>श्रेणियाँ और लेन-देन नियम</strong> — पैसे कैसे समूहित और सॉर्ट हों।</li>
      <li><strong>उपलब्धियाँ और पीयर बेंचमार्क</strong> — Progress और Coach में दिखने वाले लक्ष्य।</li>
      <li><strong>रिटायरमेंट, बीमा और निवेश</strong> — Progress टैब पर प्लानर।</li>
      <li><strong>कार्बन फ़ुटप्रिंट</strong> — Toolbox में खर्च से अनुमान।</li>
      <li><strong>दस्तावेज़ स्कैन</strong> — कागज़ ऐप में लाएँ।</li>
      <li><strong>खरीदारी विशलिस्ट</strong> — Activity हब से चाहतें सहेजें।</li>
    </ul>`,
  },
  hhh: {
    es: `<h2>También en la app</h2>
    <ul>
      <li><strong>Registro de uso y plan de rotación</strong> — qué llevas y cuándo rotar.</li>
      <li><strong>Comparar piezas</strong> — lado a lado desde Tools.</li>
      <li><strong>Listados eBay y analizador de trueques</strong> — busca anuncios y valora un trueque.</li>
      <li><strong>Lista de deseos</strong> — objetivos en My Museum y caza desde ahí.</li>
      <li><strong>Ingreso de herencias</strong> — entra un lote rápido desde la barra de Museum.</li>
      <li><strong>Seguimiento de servicio, informe de seguro, impresión/exportación y finanzas</strong> — overflow de Museum para mantenimiento, cobertura y P&amp;L.</li>
      <li><strong>Alertas de precio</strong> — vigila objetivos desde el overflow de Museum.</li>
      <li><strong>Estudio fotográfico, código de barras y escáner de documentos</strong> — captura desde Tools.</li>
      <li><strong>Pasaporte del reloj y compartir cerca</strong> — registros y compartir cercano desde Tools / Settings.</li>
      <li><strong>Herramientas de banco</strong> — timegrapher lite, beat meter, péndulo, dientes de engranaje y ayudas de movimiento.</li>
      <li><strong>Coach de coleccionista y chat</strong> — pregunta desde Home y Tools.</li>
      <li><strong>Web companion y sync de dispositivos</strong> — usa el kit desde un navegador en la misma red.</li>
      <li><strong>Pack offline para ferias</strong> — lleva registros a una feria sin depender del Wi‑Fi del local.</li>
      <li><strong>Atajos de voz</strong> — acciones manos libres desde Settings.</li>
    </ul>`,
    zh: `<h2>应用里还有</h2>
    <ul>
      <li><strong>佩戴记录与轮换计划</strong> — 你戴什么、何时轮换。</li>
      <li><strong>对比藏品</strong> — 在 Tools 并排比较。</li>
      <li><strong>eBay 列表与交易分析</strong> — 搜列表并权衡交易。</li>
      <li><strong>心愿单</strong> — 在 My Museum 保存目标再去猎寻。</li>
      <li><strong>遗产入库</strong> — 从 Museum 栏快速录入一批。</li>
      <li><strong>保养跟踪、保险报告、打印/导出与财务</strong> — Museum 更多菜单中的维护、保障与损益。</li>
      <li><strong>价格提醒</strong> — 从 Museum 更多菜单盯目标价。</li>
      <li><strong>摄影棚、条码与文档扫描</strong> — 在 Tools 采集归档。</li>
      <li><strong>手表护照与近场分享</strong> — Tools / Settings 中的护照与近距分享。</li>
      <li><strong>工作台工具</strong> — timegrapher lite、beat meter、摆锤、齿数与机芯辅助。</li>
      <li><strong>藏家教练与聊天</strong> — 从 Home 与 Tools 提问。</li>
      <li><strong>Web companion 与设备同步</strong> — 在同一网络用浏览器使用工具。</li>
      <li><strong>线下展会包</strong> — 不依赖场馆 Wi‑Fi 也能带记录参展。</li>
      <li><strong>语音快捷方式</strong> — 在 Settings 免提操作。</li>
    </ul>`,
    de: `<h2>Auch in der App</h2>
    <ul>
      <li><strong>Trageprotokoll &amp; Rotationsplaner</strong> — was du trägst und wann wechseln.</li>
      <li><strong>Stücke vergleichen</strong> — nebeneinander unter Tools.</li>
      <li><strong>eBay-Angebote &amp; Tausch-Analyse</strong> — Angebote suchen und einen Tausch abwägen.</li>
      <li><strong>Wunschliste</strong> — Ziele in My Museum, dann von dort jagen.</li>
      <li><strong>Nachlass-Aufnahme</strong> — schnell mehrere Stücke über die Museum-Leiste.</li>
      <li><strong>Service-Tracker, Versicherungsbericht, Druck/Export &amp; Finanzen</strong> — Museum-Overflow für Pflege, Absicherung und GuV.</li>
      <li><strong>Preisalarme</strong> — Ziele im Museum-Overflow beobachten.</li>
      <li><strong>Fotostudio, Barcode &amp; Dokumentenscanner</strong> — erfassen unter Tools.</li>
      <li><strong>Uhren-Pass &amp; Teilen in der Nähe</strong> — Pass und Nahe-teilen unter Tools / Settings.</li>
      <li><strong>Bankwerkzeuge</strong> — Timegrapher lite, Beat-Meter, Pendel, Zähne und Werk-Helfer.</li>
      <li><strong>Collector Coach &amp; Chat</strong> — fragen unter Home und Tools.</li>
      <li><strong>Web Companion &amp; Geräte-Sync</strong> — Toolkit im Browser im gleichen Netz.</li>
      <li><strong>Offline-Show-Pack</strong> — Unterlagen zur Börse ohne Venue-Wi‑Fi.</li>
      <li><strong>Sprachkürzel</strong> — freihändige Aktionen unter Settings.</li>
    </ul>`,
    fr: `<h2>Aussi dans l’app</h2>
    <ul>
      <li><strong>Journal de port &amp; plan de rotation</strong> — ce que vous portez et quand tourner.</li>
      <li><strong>Comparer des pièces</strong> — côte à côte depuis Tools.</li>
      <li><strong>Annonces eBay &amp; analyse d’échange</strong> — chercher et peser un échange.</li>
      <li><strong>Liste de souhaits</strong> — cibles dans My Museum, puis chasse.</li>
      <li><strong>Entrée de succession</strong> — un lot rapide depuis la barre Museum.</li>
      <li><strong>Suivi d’entretien, rapport d’assurance, impression/export &amp; finances</strong> — overflow Museum pour entretien, couverture et P&amp;L.</li>
      <li><strong>Alertes de prix</strong> — surveillez depuis l’overflow Museum.</li>
      <li><strong>Studio photo, code-barres &amp; scan de documents</strong> — capture depuis Tools.</li>
      <li><strong>Passeport montre &amp; partage à proximité</strong> — depuis Tools / Settings.</li>
      <li><strong>Outils d’établi</strong> — timegrapher lite, beat meter, pendule, dents et aides au mouvement.</li>
      <li><strong>Coach collectionneur &amp; chat</strong> — demander depuis Home et Tools.</li>
      <li><strong>Web companion &amp; sync appareils</strong> — toolkit dans un navigateur du même réseau.</li>
      <li><strong>Pack salon hors ligne</strong> — emportez des dossiers sans Wi‑Fi du lieu.</li>
      <li><strong>Raccourcis vocaux</strong> — actions mains libres dans Settings.</li>
    </ul>`,
    pt: `<h2>Também na app</h2>
    <ul>
      <li><strong>Diário de uso e plano de rotação</strong> — o que usa e quando rodar.</li>
      <li><strong>Comparar peças</strong> — lado a lado em Tools.</li>
      <li><strong>Anúncios eBay e analisador de trocas</strong> — procurar e pesar uma troca.</li>
      <li><strong>Lista de desejos</strong> — alvos em My Museum e caça a partir daí.</li>
      <li><strong>Entrada de espólio</strong> — um lote rápido na barra Museum.</li>
      <li><strong>Rasto de serviço, relatório de seguro, impressão/exportação e finanças</strong> — overflow do Museum para manutenção, cobertura e P&amp;L.</li>
      <li><strong>Alertas de preço</strong> — vigiar alvos no overflow do Museum.</li>
      <li><strong>Estúdio fotográfico, código de barras e scanner de documentos</strong> — captar em Tools.</li>
      <li><strong>Passaporte do relógio e partilha perto</strong> — em Tools / Settings.</li>
      <li><strong>Ferramentas de bancada</strong> — timegrapher lite, beat meter, pêndulo, dentes e ajudas de movimento.</li>
      <li><strong>Coach de colecionador e chat</strong> — perguntar em Home e Tools.</li>
      <li><strong>Web companion e sync de dispositivos</strong> — kit num browser na mesma rede.</li>
      <li><strong>Pack offline para feiras</strong> — levar registos sem Wi‑Fi do local.</li>
      <li><strong>Atalhos de voz</strong> — ações mãos-livres em Settings.</li>
    </ul>`,
    it: `<h2>Anche nell’app</h2>
    <ul>
      <li><strong>Registro di uso e piano di rotazione</strong> — cosa indossi e quando ruotare.</li>
      <li><strong>Confronta pezzi</strong> — affiancati da Tools.</li>
      <li><strong>Annunci eBay e analizzatore di scambi</strong> — cerca e valuta uno scambio.</li>
      <li><strong>Lista desideri</strong> — obiettivi in My Museum, poi caccia.</li>
      <li><strong>Ingresso eredità</strong> — un lotto veloce dalla barra Museum.</li>
      <li><strong>Tracker servizio, report assicurativo, stampa/export e finanze</strong> — overflow Museum per manutenzione, copertura e P&amp;L.</li>
      <li><strong>Avvisi di prezzo</strong> — tieni d’occhio i target dall’overflow Museum.</li>
      <li><strong>Photo studio, barcode e scanner documenti</strong> — acquisisci da Tools.</li>
      <li><strong>Passaporto orologio e condivisione vicina</strong> — da Tools / Settings.</li>
      <li><strong>Strumenti da banco</strong> — timegrapher lite, beat meter, pendolo, denti e aiuti al movimento.</li>
      <li><strong>Collector coach e chat</strong> — chiedi da Home e Tools.</li>
      <li><strong>Web companion e sync dispositivi</strong> — toolkit dal browser sulla stessa rete.</li>
      <li><strong>Pacchetto fiera offline</strong> — porta i record senza Wi‑Fi della sede.</li>
      <li><strong>Scorciatoie vocali</strong> — azioni a mani libere in Settings.</li>
    </ul>`,
    hi: `<h2>ऐप में और भी</h2>
    <ul>
      <li><strong>वियर लॉग और रोटेशन प्लानर</strong> — आप क्या पहनते हैं और कब बदलें।</li>
      <li><strong>टुकड़े तुलना</strong> — Tools से साइड-बाय-साइड।</li>
      <li><strong>eBay लिस्टिंग और ट्रेड विश्लेषक</strong> — लिस्ट खोजें और सौदा तौलें।</li>
      <li><strong>विशलिस्ट</strong> — My Museum में लक्ष्य, फिर वहाँ से हंट।</li>
      <li><strong>एस्टेट इनटेक</strong> — Museum बार से एक साथ कई टुकड़े।</li>
      <li><strong>सर्विस ट्रैकर, बीमा रिपोर्ट, प्रिंट/एक्सपोर्ट और वित्त</strong> — Museum ओवरफ़्लो में रखरखाव, कवर और P&amp;L।</li>
      <li><strong>कीमत अलर्ट</strong> — Museum ओवरफ़्लो से लक्ष्य देखें।</li>
      <li><strong>फ़ोटो स्टूडियो, बारकोड और दस्तावेज़ स्कैनर</strong> — Tools से कैप्चर।</li>
      <li><strong>वॉच पासपोर्ट और पास में शेयर</strong> — Tools / Settings से।</li>
      <li><strong>बेंच टूल्स</strong> — timegrapher lite, beat meter, पेंडुलम, गियर टीथ और मूवमेंट मदद।</li>
      <li><strong>कलेक्टर कोच और चैट</strong> — Home और Tools से पूछें।</li>
      <li><strong>Web companion और डिवाइस सिंक</strong> — उसी नेटवर्क के ब्राउज़र से टूलकिट।</li>
      <li><strong>ऑफ़लाइन शो पैक</strong> — जगह के Wi‑Fi के बिना रिकॉर्ड ले जाएँ।</li>
      <li><strong>वॉयस शॉर्टकट</strong> — Settings से हैंड्स-फ़्री।</li>
    </ul>`,
  },
  cvc: {
    es: `<h2>También en la app</h2>
    <ul>
      <li><strong>Comparar, analizador de trueques, eBay y mercadillos</strong> — valora un trato y busca anuncios en Tools.</li>
      <li><strong>Demand rolodex y anuncios de dealers</strong> — contactos y anuncios que te importan.</li>
      <li><strong>Ingreso de herencias</strong> — un lote desde Tools.</li>
      <li><strong>Decodificador Zippo, grading, tracker de certificados y sets</strong> — autentica y completa una serie.</li>
      <li><strong>Estudio fotográfico, código de barras y escaneo de documentos</strong> — captura en Tools.</li>
      <li><strong>Chat, web companion y pasaporte</strong> — pregunta, usa el companion y guarda un pasaporte.</li>
      <li><strong>Calendario de eventos, vista offline y rotación de display</strong> — ferias, packs offline y planificación de vitrina.</li>
      <li><strong>Informe de inventario y P&amp;L / presupuesto</strong> — franja de gestión de la colección.</li>
      <li><strong>Grail hunt desde deseos</strong> — convierte un deseo en alertas de anuncios.</li>
    </ul>`,
    zh: `<h2>应用里还有</h2>
    <ul>
      <li><strong>对比、交易分析、eBay 与跳蚤市场</strong> — 在 Tools 权衡交易并扫列表。</li>
      <li><strong>Demand 名录与经销商广告</strong> — 保存联系人与你关心的广告。</li>
      <li><strong>遗产入库</strong> — 从 Tools 批量录入。</li>
      <li><strong>Zippo 解码、评级、证书跟踪与套系完成</strong> — 鉴定并凑齐一套。</li>
      <li><strong>摄影棚、条码与文档扫描</strong> — 在 Tools 采集。</li>
      <li><strong>聊天、web companion 与护照</strong> — 提问、浏览器伴侣与护照记录。</li>
      <li><strong>活动日历、离线查看与陈列轮换</strong> — 展会、离线包与陈列规划。</li>
      <li><strong>库存报告与损益 / 预算</strong> — 收藏管理条中的报告与资金视图。</li>
      <li><strong>从心愿开启 Grail hunt</strong> — 把心愿变成列表提醒。</li>
    </ul>`,
    de: `<h2>Auch in der App</h2>
    <ul>
      <li><strong>Vergleich, Tausch-Analyse, eBay &amp; Flohmärkte</strong> — Deal abwägen und Angebote unter Tools scannen.</li>
      <li><strong>Demand-Rolodex &amp; Händleranzeigen</strong> — Kontakte und Anzeigen behalten.</li>
      <li><strong>Nachlass-Aufnahme</strong> — Charge unter Tools.</li>
      <li><strong>Zippo-Decoder, Grading, Zert-Tracker &amp; Set-Vervollständigung</strong> — authentifizieren und Sets füllen.</li>
      <li><strong>Fotostudio, Barcode &amp; Dokumentenscan</strong> — unter Tools erfassen.</li>
      <li><strong>Chat, Web Companion &amp; Pass</strong> — fragen, Companion nutzen, Pass führen.</li>
      <li><strong>Eventkalender, Offline-Ansicht &amp; Display-Rotation</strong> — Shows, Offline-Packs, Vitrinenplanung.</li>
      <li><strong>Inventarbericht &amp; GuV / Budget</strong> — Management-Leiste der Sammlung.</li>
      <li><strong>Grail Hunt aus Wünschen</strong> — Wunsch zu Angebotsalarmen.</li>
    </ul>`,
    fr: `<h2>Aussi dans l’app</h2>
    <ul>
      <li><strong>Comparer, analyse d’échange, eBay &amp; brocantes</strong> — peser un deal et scanner depuis Tools.</li>
      <li><strong>Demand rolodex &amp; annonces dealers</strong> — contacts et annonces qui comptent.</li>
      <li><strong>Entrée de succession</strong> — un lot depuis Tools.</li>
      <li><strong>Décodeur Zippo, grading, suivi de certificats &amp; sets</strong> — authentifier et finir une série.</li>
      <li><strong>Studio photo, code-barres &amp; scan de documents</strong> — capturer dans Tools.</li>
      <li><strong>Chat, web companion &amp; passeport</strong> — demander, companion et passeport.</li>
      <li><strong>Calendrier d’événements, hors ligne &amp; rotation d’affichage</strong> — salons, packs hors ligne, vitrine.</li>
      <li><strong>Rapport d’inventaire &amp; P&amp;L / budget</strong> — bandeau de gestion de collection.</li>
      <li><strong>Grail hunt depuis un souhait</strong> — un souhait devient alertes d’annonces.</li>
    </ul>`,
    pt: `<h2>Também na app</h2>
    <ul>
      <li><strong>Comparar, analisador de trocas, eBay e feiras</strong> — pesar um negócio e varrer anúncios em Tools.</li>
      <li><strong>Demand rolodex e anúncios de dealers</strong> — contactos e anúncios que importam.</li>
      <li><strong>Entrada de espólio</strong> — um lote em Tools.</li>
      <li><strong>Descodificador Zippo, grading, tracker de certificados e sets</strong> — autenticar e completar uma série.</li>
      <li><strong>Estúdio fotográfico, código de barras e scan de documentos</strong> — captar em Tools.</li>
      <li><strong>Chat, web companion e passaporte</strong> — perguntar, companion e passaporte.</li>
      <li><strong>Calendário de eventos, vista offline e rotação de display</strong> — feiras, packs offline e vitrina.</li>
      <li><strong>Relatório de inventário e P&amp;L / orçamento</strong> — faixa de gestão da coleção.</li>
      <li><strong>Grail hunt a partir do desejo</strong> — um desejo vira alertas de anúncios.</li>
    </ul>`,
    it: `<h2>Anche nell’app</h2>
    <ul>
      <li><strong>Confronta, analizzatore di scambi, eBay e mercatini</strong> — valuta un affare e scansiona da Tools.</li>
      <li><strong>Demand rolodex e annunci dealer</strong> — contatti e annunci che contano.</li>
      <li><strong>Ingresso eredità</strong> — un lotto da Tools.</li>
      <li><strong>Decoder Zippo, grading, tracker certificati e set</strong> — autentica e completa una serie.</li>
      <li><strong>Photo studio, barcode e scan documenti</strong> — acquisisci in Tools.</li>
      <li><strong>Chat, web companion e passaporto</strong> — chiedi, companion e passaporto.</li>
      <li><strong>Calendario eventi, vista offline e rotazione display</strong> — fiere, pack offline e vetrina.</li>
      <li><strong>Report inventario e P&amp;L / budget</strong> — striscia di gestione collezione.</li>
      <li><strong>Grail hunt dal desiderio</strong> — un desiderio diventa avvisi di annunci.</li>
    </ul>`,
    hi: `<h2>ऐप में और भी</h2>
    <ul>
      <li><strong>तुलना, ट्रेड विश्लेषक, eBay और फ़्लीया बाज़ार</strong> — Tools से सौदा तौलें और लिस्ट स्कैन करें।</li>
      <li><strong>Demand रोलोडेक्स और डीलर विज्ञापन</strong> — संपर्क और ज़रूरी विज्ञापन रखें।</li>
      <li><strong>एस्टेट इनटेक</strong> — Tools से बैच जोड़ें।</li>
      <li><strong>Zippo डिकोडर, ग्रेडिंग, सर्ट ट्रैकर और सेट पूरा करना</strong> — प्रमाणित करें और सेट पूरा करें।</li>
      <li><strong>फ़ोटो स्टूडियो, बारकोड और दस्तावेज़ स्कैन</strong> — Tools में कैप्चर।</li>
      <li><strong>चैट, web companion और पासपोर्ट</strong> — पूछें, companion और पासपोर्ट।</li>
      <li><strong>इवेंट कैलेंडर, ऑफ़लाइन व्यू और डिस्प्ले रोटेशन</strong> — शो, ऑफ़लाइन पैक, डिस्प्ले प्लान।</li>
      <li><strong>इन्वेंटरी रिपोर्ट और P&amp;L / बजट</strong> — कलेक्शन मैनेज स्ट्रिप।</li>
      <li><strong>विशलिस्ट से Grail hunt</strong> — इच्छा को लिस्टिंग अलर्ट बनाएँ।</li>
    </ul>`,
  },
  unscribe: {
    es: `<h2>También en la app</h2>
    <ul>
      <li><strong>Calendario</strong> — calendario de renovaciones desde Inicio.</li>
      <li><strong>Insights</strong> — gráficos de gasto desde Inicio.</li>
      <li><strong>Selecciones populares</strong> — empieza por suscripciones habituales al añadir.</li>
      <li><strong>Alta manual o por voz</strong> — añade sin extracto.</li>
      <li><strong>Bloqueo de app</strong> — bloquea la app desde Settings.</li>
      <li><strong>Copia con contraseña y restaurar archivo</strong> — un archivo de copia que controlas desde Settings.</li>
      <li><strong>Confirmar cargos (Pro)</strong> — confirma qué llegó a la tarjeta desde Settings.</li>
    </ul>`,
    zh: `<h2>应用里还有</h2>
    <ul>
      <li><strong>日历</strong> — 从首页查看续订日历。</li>
      <li><strong>洞察</strong> — 从首页看支出图表。</li>
      <li><strong>热门选择</strong> — 添加时从常见订阅开始。</li>
      <li><strong>手动或语音添加</strong> — 无需对账单也可添加。</li>
      <li><strong>应用锁定</strong> — 在 Settings 锁定应用。</li>
      <li><strong>密码备份与恢复文件</strong> — 在 Settings 保管你控制的备份文件。</li>
      <li><strong>确认扣款（Pro）</strong> — 在 Settings 确认卡上的扣款。</li>
    </ul>`,
    de: `<h2>Auch in der App</h2>
    <ul>
      <li><strong>Kalender</strong> — Verlängerungskalender von Home.</li>
      <li><strong>Insights</strong> — Ausgaben-Diagramme von Home.</li>
      <li><strong>Beliebte Auswahl</strong> — starte mit gängigen Abos beim Hinzufügen.</li>
      <li><strong>Manuell oder per Sprache</strong> — Abo ohne Kontoauszug hinzufügen.</li>
      <li><strong>App-Sperre</strong> — App unter Settings sperren.</li>
      <li><strong>Passwort-Backup &amp; Datei wiederherstellen</strong> — Backup-Datei unter Settings, die du kontrollierst.</li>
      <li><strong>Belastungen bestätigen (Pro)</strong> — Kartenabbuchungen unter Settings bestätigen.</li>
    </ul>`,
    fr: `<h2>Aussi dans l’app</h2>
    <ul>
      <li><strong>Calendrier</strong> — calendrier des renouvellements depuis Accueil.</li>
      <li><strong>Insights</strong> — graphiques de dépenses depuis Accueil.</li>
      <li><strong>Choix populaires</strong> — partez d’abonnements courants à l’ajout.</li>
      <li><strong>Ajout manuel ou vocal</strong> — ajoutez sans relevé.</li>
      <li><strong>Verrouillage de l’app</strong> — verrouillez dans Settings.</li>
      <li><strong>Sauvegarde par mot de passe &amp; restaurer un fichier</strong> — un fichier de sauvegarde que vous contrôlez dans Settings.</li>
      <li><strong>Confirmer les prélèvements (Pro)</strong> — confirmez ce qui a été débité dans Settings.</li>
    </ul>`,
    pt: `<h2>Também na app</h2>
    <ul>
      <li><strong>Calendário</strong> — calendário de renovações no Início.</li>
      <li><strong>Insights</strong> — gráficos de gasto no Início.</li>
      <li><strong>Escolhas populares</strong> — comece por subscrições comuns ao adicionar.</li>
      <li><strong>Adicionar à mão ou por voz</strong> — adicione sem extrato.</li>
      <li><strong>Bloqueio da app</strong> — bloqueie em Settings.</li>
      <li><strong>Cópia com palavra-passe e restaurar ficheiro</strong> — um ficheiro de cópia que controla em Settings.</li>
      <li><strong>Confirmar cobranças (Pro)</strong> — confirme o que caiu no cartão em Settings.</li>
    </ul>`,
    it: `<h2>Anche nell’app</h2>
    <ul>
      <li><strong>Calendario</strong> — calendario rinnovi da Home.</li>
      <li><strong>Insights</strong> — grafici di spesa da Home.</li>
      <li><strong>Scelte popolari</strong> — parti da abbonamenti comuni quando aggiungi.</li>
      <li><strong>Aggiunta manuale o vocale</strong> — aggiungi senza estratto.</li>
      <li><strong>Blocco app</strong> — blocca l’app da Settings.</li>
      <li><strong>Backup con password e ripristino file</strong> — un file di backup che controlli da Settings.</li>
      <li><strong>Conferma addebiti (Pro)</strong> — conferma cosa è arrivato sulla carta da Settings.</li>
    </ul>`,
    hi: `<h2>ऐप में और भी</h2>
    <ul>
      <li><strong>कैलेंडर</strong> — होम से नवीनीकरण कैलेंडर।</li>
      <li><strong>इनसाइट्स</strong> — होम से खर्च चार्ट।</li>
      <li><strong>लोकप्रिय विकल्प</strong> — जोड़ते समय आम सदस्यताओं से शुरू करें।</li>
      <li><strong>मैनुअल या वॉयस ऐड</strong> — स्टेटमेंट के बिना जोड़ें।</li>
      <li><strong>ऐप लॉक</strong> — Settings से ऐप लॉक करें।</li>
      <li><strong>पासवर्ड बैकअप और फ़ाइल रिस्टोर</strong> — Settings से आपके नियंत्रण वाली बैकअप फ़ाइल।</li>
      <li><strong>चार्ज पुष्टि (Pro)</strong> — Settings से कार्ड पर क्या कटा पुष्टि करें।</li>
    </ul>`,
  },
};

const ANCHORS = {
  pbj: {
    // after Stay private / Stay private locale variants — insert before Premium heading
    re: /(<h2[^>]*>\s*(?:Premium|Premium\b)[^<]*<\/h2>)/i,
  },
  hhh: {
    re: /(<h2[^>]*>\s*(?:Who it is for|Para quién es|适合谁|Für wen|Pour qui|Para quem|Per chi è|किसके लिए)<\/h2>)/,
  },
  cvc: {
    re: /(<h2[^>]*>\s*(?:Guides|Guías|指南|Leitfäden|Guides|Guias|Guide|गाइड)[^<]*<\/h2>)/i,
  },
  unscribe: {
    re: /(<h2[^>]*>\s*(?:Pro)\s*<\/h2>)/i,
  },
};

function insertBlock(file, app, lang) {
  let html = fs.readFileSync(file, 'utf8');
  if (html.includes('También en la app') || html.includes('应用里还有') || html.includes('Auch in der App') || html.includes('Aussi dans') || html.includes('Também na app') || html.includes('Anche nell') || html.includes('ऐप में और भी') || html.includes('Also in the app')) {
    // already has a section — skip if our h2 present
    if (html.includes(`<h2>${H2[lang]}</h2>`) || html.includes('Also in the app')) {
      return 'skip';
    }
  }
  const block = BLOCKS[app][lang];
  const anchor = ANCHORS[app];
  if (!anchor.re.test(html)) {
    console.warn('anchor miss', path.relative(ROOT, file));
    return 'miss';
  }
  html = html.replace(anchor.re, `\n    ${block}\n\n    $1`);
  fs.writeFileSync(file, html, 'utf8');
  return 'ok';
}

function patchOneFind(app, lang) {
  const file = path.join(ROOT, app, lang, 'index.html');
  if (!fs.existsSync(file)) return;
  let html = fs.readFileSync(file, 'utf8');
  const line = ONE_FIND[lang];
  if (html.includes(line)) return;
  // Append to the official-stores price note paragraph if present
  const re = /(<p class="note rise rise-5">)([^<]*\$\/(?:mes|Monat|mois|mês|mese|महीना)[^<]*|[^<]*\$\/año[^<]*|[^<]*\$\/Jahr[^<]*|[^<]*\$\/an[^<]*|[^<]*\$\/ano[^<]*|[^<]*\$\/anno[^<]*|[^<]*\/वर्ष[^<]*|[^<]*74[,.]99[^<]*)(<\/p>)/;
  // Simpler: find note with 9,99 or 74,99 or $9.99 in rise-5
  const re2 = /(<p class="note rise rise-5">)([\s\S]*?)(<\/p>)/;
  let replaced = false;
  html = html.replace(re2, (m, a, body, c) => {
    if (replaced) return m;
    if (!/9[,.]99|74[,.]99|14/.test(body)) return m;
    if (body.includes(line) || /One good find|Un buen hallazgo|一次好发现|Ein guter Fund|Une bonne trouvaille|Um bom achado|Un buon ritrovo|एक अच्छी खोज/.test(body)) {
      replaced = true;
      return m;
    }
    replaced = true;
    const trimmed = body.trim().replace(/\s+$/, '');
    const sep = /[.。]$/.test(trimmed) ? ' ' : '. ';
    return `${a}${trimmed}${sep}${line}${c}`;
  });
  if (replaced) fs.writeFileSync(file, html, 'utf8');
}

let ok = 0, skip = 0, miss = 0;
for (const app of ['pbj', 'hhh', 'cvc', 'unscribe']) {
  for (const lang of LANGS) {
    const f = path.join(ROOT, app, lang, 'index.html');
    const r = insertBlock(f, app, lang);
    if (r === 'ok') ok++;
    else if (r === 'skip') skip++;
    else miss++;
  }
}
for (const app of ['hhh', 'cvc']) {
  for (const lang of LANGS) patchOneFind(app, lang);
}
console.log({ ok, skip, miss });
