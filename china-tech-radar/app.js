/**
 * Dual & Multi-Collection EV & NEV Automotive Intelligence Catalog
 * Collections:
 * 1. Europe Top 500 (ADAC / ACEA / JATO - Alle Marken)
 * 2. China Top 500 (Dongchedi / CPCA / Autohome - 纯自主品牌)
 * 3. BMW Electrified Fleet (Alle 53 existierenden BEV & PHEV Modelle mit Preislisten & ADAC)
 */

(function () {
  'use strict';

  // State Management
  let currentMarket = 'EU'; // 'EU', 'CN', 'BMW'
  let allVehicles = [];
  let filteredVehicles = [];

  const filters = {
    search: '',
    powertrain: 'ALL',
    brand: 'ALL',
    bodyType: 'ALL',
    drive: 'ALL',
    towing: 0,
    equipment: 'ALL',
    maxPrice: 300000,
    minRange: 0,
    sortKey: 'rank',
    sortDir: 'asc',
    studyCohort: 'ALL'
  };

  // DOM Elements
  const elements = {
    // Market Selectors
    marketToggleEu: document.getElementById('market-toggle-eu'),
    marketToggleCn: document.getElementById('market-toggle-cn'),
    marketToggleBmw: document.getElementById('market-toggle-bmw'),

    // Dynamic Header Elements
    headerBadgeRegion: document.getElementById('header-badge-region'),
    headerBadgeSources: document.getElementById('header-badge-sources'),
    headerMainTitle: document.getElementById('header-main-title'),
    headerSubtitle: document.getElementById('header-subtitle'),
    btnCatalogLink: document.getElementById('btn-catalog-link'),
    btnCatalogLabel: document.getElementById('btn-catalog-label'),
    btnExportCsvLabel: document.getElementById('btn-export-csv-label'),
    btnExportJsonLabel: document.getElementById('btn-export-json-label'),

    // KPIs
    kpiTotalModels: document.getElementById('kpi-total-models'),
    kpiSubModels: document.getElementById('kpi-sub-models'),
    kpiTotalVolume: document.getElementById('kpi-total-volume'),
    kpiLabelVolume: document.getElementById('kpi-label-volume'),
    kpiSubVolume: document.getElementById('kpi-sub-volume'),
    kpiPowertrainSplit: document.getElementById('kpi-powertrain-split'),
    kpiBevPct: document.getElementById('kpi-bev-pct'),
    kpiAvgMetrics: document.getElementById('kpi-avg-metrics'),
    kpiLabelMetrics: document.getElementById('kpi-label-metrics'),
    kpiSubMetrics: document.getElementById('kpi-sub-metrics'),

    // Table Header Labels
    thLabelSales: document.getElementById('th-label-sales'),
    thLabelShare: document.getElementById('th-label-share'),
    thLabelPrice: document.getElementById('th-label-price'),
    thLabelRange: document.getElementById('th-label-range'),
    thLabelTowing: document.getElementById('th-label-towing'),
    thLabelDc: document.getElementById('th-label-dc'),
    thLabelHighlights: document.getElementById('th-label-highlights'),
    thLabelActions: document.getElementById('th-label-actions'),

    // Table & Controls
    tableBody: document.getElementById('table-body'),
    emptyState: document.getElementById('empty-state'),
    inputSearch: document.getElementById('input-search'),
    searchCount: document.getElementById('search-result-count'),
    paginationInfo: document.getElementById('pagination-info'),
    selectBrand: document.getElementById('select-brand'),
    selectBody: document.getElementById('select-body'),
    selectDrive: document.getElementById('select-drive'),
    selectTowing: document.getElementById('select-towing'),
    selectEquipment: document.getElementById('select-equipment'),
    selectSort: document.getElementById('select-sort'),
    rangeMaxPrice: document.getElementById('range-max-price'),
    displayMaxPrice: document.getElementById('display-max-price'),
    rangeMinRange: document.getElementById('range-min-range'),
    displayMinRange: document.getElementById('display-min-range'),
    btnReset: document.getElementById('btn-reset-filters'),
    btnEmptyReset: document.getElementById('btn-empty-reset'),
    btnExportCsv: document.getElementById('btn-export-csv'),
    btnExportJson: document.getElementById('btn-export-json'),
    btnExportMatching: document.getElementById('btn-export-matching'),
    btnExportPdf: document.getElementById('btn-export-pdf'),
    btnExportPipelineCsv: document.getElementById('btn-export-pipeline-csv'),
    bmwStudyFilterBar: document.getElementById('bmw-study-filter-bar'),
    studyChips: document.querySelectorAll('.study-chip'),
    powertrainPills: document.querySelectorAll('[data-filter-powertrain]'),
    sortableHeaders: document.querySelectorAll('th.sortable'),

    // Methodology
    methodologyTitle: document.getElementById('methodology-title'),
    methodologyGrid: document.getElementById('methodology-grid'),

    // Modal
    modal: document.getElementById('detail-modal'),
    modalCloseBtn: document.getElementById('modal-close-btn'),
    modalTabs: document.querySelectorAll('.modal-tab-btn'),
    modalTabPanes: document.querySelectorAll('.modal-tab-pane'),
    modalRankBadge: document.getElementById('modal-rank-badge'),
    modalTypeBadge: document.getElementById('modal-type-badge'),
    modalSegmentBadge: document.getElementById('modal-segment-badge'),
    modalTitle: document.getElementById('modal-title'),
    modalVariant: document.getElementById('modal-variant'),
    modalUspsList: document.getElementById('modal-usps-list'),
    modalInteriorList: document.getElementById('modal-interior-list'),
    modalExteriorList: document.getElementById('modal-exterior-list'),
    modalAssistanceList: document.getElementById('modal-assistance-list'),
    modalTowing: document.getElementById('modal-towing'),
    modalFrunk: document.getElementById('modal-frunk'),
    modalTrunk: document.getElementById('modal-trunk'),
    modalHeatpump: document.getElementById('modal-heatpump'),
    modalChargeTime: document.getElementById('modal-chargetime'),
    modalHud: document.getElementById('modal-hud'),
    modalAudio: document.getElementById('modal-audio'),
    modalSales: document.getElementById('modal-sales'),
    modalShare: document.getElementById('modal-share'),
    modalPrice: document.getElementById('modal-price'),
    modalRange: document.getElementById('modal-range'),
    modalBattery: document.getElementById('modal-battery'),
    modalPower: document.getElementById('modal-power'),
    modalDrive: document.getElementById('modal-drive'),
    modalDc: document.getElementById('modal-dc'),
    modalAccel: document.getElementById('modal-accel'),
    modalTopSpeed: document.getElementById('modal-topspeed'),
    modalEfficiency: document.getElementById('modal-efficiency'),
    modalBodyType: document.getElementById('modal-bodytype'),
    modalEvidence: document.getElementById('modal-evidence'),
    modalFooterContainer: document.getElementById('modal-footer-container'),
    modalFeedbackBtn: document.getElementById('modal-tab-feedback-btn'),
    modalFeedbackContent: document.getElementById('modal-feedback-content')
  };

  // Formatters
  const formatNumber = num => new Intl.NumberFormat('de-DE').format(num);
  const formatCurrency = num => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(num);

  /**
   * Initialize App Data
   */
  async function init() {
    bindEventListeners();
    setMarket('EU');
  }

  /**
   * Switch Active Dataset / Collection
   */
  function setMarket(market) {
    currentMarket = market;

    // Update Toggle Buttons UI
    if (elements.marketToggleEu) {
      elements.marketToggleEu.classList.toggle('active', market === 'EU');
      elements.marketToggleEu.setAttribute('aria-selected', market === 'EU');
    }
    if (elements.marketToggleCn) {
      elements.marketToggleCn.classList.toggle('active', market === 'CN');
      elements.marketToggleCn.setAttribute('aria-selected', market === 'CN');
    }
    if (elements.marketToggleBmw) {
      elements.marketToggleBmw.classList.toggle('active', market === 'BMW');
      elements.marketToggleBmw.setAttribute('aria-selected', market === 'BMW');
    }

    // Select Data Source
    if (market === 'EU') {
      if (window.TOP_500_DATA) {
        allVehicles = Array.isArray(window.TOP_500_DATA) ? window.TOP_500_DATA : (window.TOP_500_DATA.cars || []);
      }
      applyEuMarketHeader();
    } else if (market === 'CN') {
      if (window.TOP_500_CHINA_DATA) {
        allVehicles = Array.isArray(window.TOP_500_CHINA_DATA) ? window.TOP_500_CHINA_DATA : (window.TOP_500_CHINA_DATA.cars || []);
      }
      applyCnMarketHeader();
    } else if (market === 'BMW') {
      if (window.BMW_DATA) {
        allVehicles = Array.isArray(window.BMW_DATA) ? window.BMW_DATA : (window.BMW_DATA.cars || []);
      }
      applyBmwMarketHeader();
    }

    // Reset filters and sort
    resetFilters();
  }

  /**
   * Apply European Market Headers & KPIs
   */
  function applyEuMarketHeader() {
    if (elements.headerBadgeRegion) elements.headerBadgeRegion.textContent = 'European Market Intelligence';
    if (elements.headerBadgeSources) elements.headerBadgeSources.textContent = 'ACEA • JATO • KBA • ADAC';
    if (elements.headerMainTitle) {
      elements.headerMainTitle.innerHTML = 'Top 500 Bestselling <span class="gradient-text">EV & PHEV</span> Cars in Europe';
    }
    if (elements.headerSubtitle) {
      elements.headerSubtitle.innerHTML = 'Evidence-backed registration data across all brands in Europe (EU 27 + EFTA + UK), fully mapped with <strong>ADAC Autokatalog</strong> technical specifications, battery sizes, WLTP range, and direct model links.';
    }

    if (elements.btnCatalogLink) elements.btnCatalogLink.href = 'https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/?sort=SORTING_DESC';
    if (elements.btnCatalogLabel) elements.btnCatalogLabel.textContent = 'ADAC Autokatalog (Zulassungen absteigend)';
    if (elements.btnExportCsvLabel) elements.btnExportCsvLabel.textContent = 'Export CSV (Europe)';
    if (elements.btnExportJsonLabel) elements.btnExportJsonLabel.textContent = 'Export JSON (Europe)';
    if (elements.btnExportMatching) elements.btnExportMatching.style.display = 'none';
    if (elements.btnExportPdf) elements.btnExportPdf.style.display = 'none';
    if (elements.btnExportPipelineCsv) elements.btnExportPipelineCsv.style.display = 'none';
    if (elements.bmwStudyFilterBar) elements.bmwStudyFilterBar.classList.add('hidden');
    filters.studyCohort = 'ALL';

    // KPIs
    if (elements.kpiTotalModels) elements.kpiTotalModels.textContent = '500';
    if (elements.kpiSubModels) elements.kpiSubModels.textContent = 'Across 65+ European brands';
    if (elements.kpiLabelVolume) elements.kpiLabelVolume.textContent = 'Total European Deliveries';
    if (elements.kpiTotalVolume) elements.kpiTotalVolume.textContent = '4,188,985';
    if (elements.kpiSubVolume) elements.kpiSubVolume.textContent = 'Annual units registered in Europe';
    if (elements.kpiPowertrainSplit) elements.kpiPowertrainSplit.textContent = '338 BEV / 162 PHEV';
    if (elements.kpiBevPct) elements.kpiBevPct.textContent = '68% Pure Electric • 32% Plug-in';
    if (elements.kpiLabelMetrics) elements.kpiLabelMetrics.textContent = 'Average Range & Price';
    if (elements.kpiAvgMetrics) elements.kpiAvgMetrics.textContent = '480 km • 68,765 €';
    if (elements.kpiSubMetrics) elements.kpiSubMetrics.textContent = 'WLTP Electric BEV Range • Avg Base Price';

    // Table Headers
    if (elements.thLabelSales) elements.thLabelSales.textContent = 'European Sales / Yr';
    if (elements.thLabelShare) elements.thLabelShare.textContent = 'Market Share';
    if (elements.thLabelPrice) elements.thLabelPrice.textContent = 'ADAC Price';
    if (elements.thLabelRange) elements.thLabelRange.textContent = 'WLTP Range';
    if (elements.thLabelTowing) elements.thLabelTowing.textContent = 'Towing';
    if (elements.thLabelDc) elements.thLabelDc.textContent = 'DC Fast';
    if (elements.thLabelHighlights) elements.thLabelHighlights.textContent = 'Preisliste Highlights';
    if (elements.thLabelActions) elements.thLabelActions.textContent = 'Catalog Link';

    if (elements.inputSearch) elements.inputSearch.placeholder = 'Search by brand, model, trim (e.g., Tesla, Model Y, Long Range, eDrive20, Kuga)...';

    // Sliders
    elements.rangeMaxPrice.max = 300000;
    elements.rangeMaxPrice.step = 5000;
    elements.rangeMaxPrice.value = 300000;
    elements.displayMaxPrice.textContent = 'No Limit';

    elements.rangeMinRange.max = 800;
    elements.rangeMinRange.step = 25;
    elements.rangeMinRange.value = 0;
    elements.displayMinRange.textContent = 'Any Range';

    // Methodology Card (Europe)
    if (elements.methodologyTitle) elements.methodologyTitle.textContent = 'Ranking Methodology & Evidence Criteria (Europe)';
    if (elements.methodologyGrid) {
      elements.methodologyGrid.innerHTML = `
        <div class="methodology-item">
          <h4>1. Verified European Market Volume</h4>
          <p>Annual deliveries and registrations encompassing the entire European market (EU 27 + EFTA countries: Norway, Switzerland, Iceland + UK). Source benchmarks correlate directly with published full-year statistics from <strong>JATO Dynamics</strong>, <strong>ACEA (European Automobile Manufacturers’ Association)</strong>, and <strong>Dataforce</strong>.</p>
        </div>
        <div class="methodology-item">
          <h4>2. Powertrain Specificity (BEV vs PHEV)</h4>
          <p>Encompasses both Battery Electric Vehicles (100% BEV) and Plug-in Hybrid Electric Vehicles (PHEV with external charging capability). Trims are partitioned by real-world powertrain delivery proportions (e.g. Tesla Model Y Long Range AWD vs Standard RWD; Volvo EX30 Single Motor ER vs Twin Motor).</p>
        </div>
        <div class="methodology-item">
          <h4>3. ADAC Autokatalog Synchronization</h4>
          <p>Each model links directly to the corresponding vehicle entry in the official <strong>ADAC Autokatalog</strong> (Germany's comprehensive vehicle database), cross-referencing MSRP (€ Grundpreis in Germany/EU), net battery capacity (kWh), WLTP electric range (km), maximum DC fast-charging capacity (kW), and acceleration metrics.</p>
        </div>
      `;
    }
  }

  /**
   * Apply China Market Headers & KPIs
   */
  function applyCnMarketHeader() {
    if (elements.headerBadgeRegion) elements.headerBadgeRegion.textContent = 'China Domestic NEV Intelligence';
    if (elements.headerBadgeSources) elements.headerBadgeSources.textContent = '懂车帝 • 乘联会 CPCA • 汽车之家';
    if (elements.headerMainTitle) {
      elements.headerMainTitle.innerHTML = 'Top 500 Bestselling <span class="gradient-text">NEV Cars in China</span> (纯自主品牌)';
    }
    if (elements.headerSubtitle) {
      elements.headerSubtitle.innerHTML = 'Evidence-backed retail sales volume & technical specifications for <strong>Chinese domestic brands only</strong> (纯自主品牌 / 华系新能源), cross-referenced with <strong>懂车帝 Dongchedi</strong>, <strong>乘联会 CPCA</strong>, and <strong>汽车之家 Autohome</strong> parameters (CLTC, 800V SiC, 激光雷达, 华为ADS/小鹏XNGP/理想AD Max).';
    }

    if (elements.btnCatalogLink) elements.btnCatalogLink.href = 'https://www.dongchedi.com/sales/car-3-x-x-x-x-x';
    if (elements.btnCatalogLabel) elements.btnCatalogLabel.textContent = '懂车帝新能源零售销量总榜';
    if (elements.btnExportCsvLabel) elements.btnExportCsvLabel.textContent = 'Export CSV (China)';
    if (elements.btnExportJsonLabel) elements.btnExportJsonLabel.textContent = 'Export JSON (China)';
    if (elements.btnExportMatching) elements.btnExportMatching.style.display = 'none';
    if (elements.btnExportPdf) elements.btnExportPdf.style.display = 'none';
    if (elements.btnExportPipelineCsv) elements.btnExportPipelineCsv.style.display = 'none';
    if (elements.bmwStudyFilterBar) elements.bmwStudyFilterBar.classList.add('hidden');
    filters.studyCohort = 'ALL';

    // KPIs
    if (elements.kpiTotalModels) elements.kpiTotalModels.textContent = '500';
    if (elements.kpiSubModels) elements.kpiSubModels.textContent = 'Across 35+ 纯自主品牌 (BYD, 小米, 问界, 极氪...)';
    if (elements.kpiLabelVolume) elements.kpiLabelVolume.textContent = 'Total Accounted Deliveries';
    if (elements.kpiTotalVolume) elements.kpiTotalVolume.textContent = '9,402,531';
    if (elements.kpiSubVolume) elements.kpiSubVolume.textContent = 'Annual retail units delivered in China';
    if (elements.kpiPowertrainSplit) elements.kpiPowertrainSplit.textContent = '297 BEV / 203 PHEV & EREV';
    if (elements.kpiBevPct) elements.kpiBevPct.textContent = '59.4% 纯电动 • 40.6% 插混/增程';
    if (elements.kpiLabelMetrics) elements.kpiLabelMetrics.textContent = 'Avg Range & Price';
    if (elements.kpiAvgMetrics) elements.kpiAvgMetrics.textContent = '612 km CLTC • 19.8 万元 (~25.3k €)';
    if (elements.kpiSubMetrics) elements.kpiSubMetrics.textContent = 'CLTC Electric Range • 华系纯自主品牌平均指导价';

    // Table Headers
    if (elements.thLabelSales) elements.thLabelSales.textContent = 'China Retail Sales / Yr';
    if (elements.thLabelShare) elements.thLabelShare.textContent = 'Market Share';
    if (elements.thLabelPrice) elements.thLabelPrice.textContent = '指导价 (万元 / €)';
    if (elements.thLabelRange) elements.thLabelRange.textContent = 'CLTC Range';
    if (elements.thLabelTowing) elements.thLabelTowing.textContent = 'Towing / 空悬';
    if (elements.thLabelDc) elements.thLabelDc.textContent = '800V / 快充';
    if (elements.thLabelHighlights) elements.thLabelHighlights.textContent = '核心卖点 & 智驾座舱';
    if (elements.thLabelActions) elements.thLabelActions.textContent = '懂车帝 / 汽车之家';

    if (elements.inputSearch) elements.inputSearch.placeholder = 'Search by brand, model, chip, LiDAR (e.g. 小米, SU7, 比亚迪, 问界, 极氪, 800V, 激光雷达, 8295, 华为ADS)...';

    // Sliders
    elements.rangeMaxPrice.max = 200000;
    elements.rangeMaxPrice.step = 2500;
    elements.rangeMaxPrice.value = 200000;
    elements.displayMaxPrice.textContent = 'No Limit';

    elements.rangeMinRange.max = 1000;
    elements.rangeMinRange.step = 50;
    elements.rangeMinRange.value = 0;
    elements.displayMinRange.textContent = 'Any Range';

    // Methodology Card (China)
    if (elements.methodologyTitle) elements.methodologyTitle.textContent = '榜单统计方法与数据源证据 (中国纯自主品牌新能源)';
    if (elements.methodologyGrid) {
      elements.methodologyGrid.innerHTML = `
        <div class="methodology-item">
          <h4>1. 懂车帝零售销量榜与乘联会权威数据</h4>
          <p>销量数据基于<strong>懂车帝 (Dongchedi)</strong> 汽车零售销量权威大数据库与<strong>乘联会 (CPCA)</strong> 全国乘用车市场信息联席会最新月度/年度真实零售上险数据，客观反映中国新能源汽车市场终端口碑与销量格局。</p>
        </div>
        <div class="methodology-item">
          <h4>2. 严格限定“纯中国自主品牌”</h4>
          <p>严格剔除合资与外资品牌（特斯拉 Tesla、大众 ID.、宝马 i、奔驰 EQ、丰田等），仅收录<strong>纯中国本土自主新能源品牌 (华系新能源)</strong>，覆盖比亚迪王朝/海洋、小米汽车、鸿蒙智行 (问界/智界/享界)、理想、极氪、小鹏、蔚来/乐道、零跑、深蓝、腾势、吉利银河、五菱、长安启源、长城坦克/魏牌等。</p>
        </div>
        <div class="methodology-item">
          <h4>3. 汽车之家参数配置全量对齐</h4>
          <p>深度对齐<strong>汽车之家 (Autohome)</strong> 车型参数配置表，涵盖 CLTC 纯电续航、碳化硅高压架构 (800V SiC / 400V)、激光雷达搭载量、华为乾崑 ADS 3.0 / 小鹏 XNGP / 理想 AD Max 端到端智驾大模型，以及高通骁龙 8295 / 鸿蒙 HarmonyOS / 小米澎湃 HyperOS 智能座舱生态。</p>
        </div>
      `;
    }
  }

  /**
   * Apply BMW Fleet Headers & KPIs
   */
  function applyBmwMarketHeader() {
    if (elements.headerBadgeRegion) elements.headerBadgeRegion.textContent = 'BMW Group Electrified Fleet';
    if (elements.headerBadgeSources) elements.headerBadgeSources.textContent = 'BMW Preislisten • KBA • ACEA • ADAC';
    if (elements.headerMainTitle) {
      elements.headerMainTitle.innerHTML = 'BMW Fleet: All <span class="gradient-text">EV & PHEV Models</span> (53 Variants)';
    }
    if (elements.headerSubtitle) {
      elements.headerSubtitle.innerHTML = 'Complete enumeration of all 53 existing battery-electric (BEV) and plug-in hybrid (PHEV) models by <strong>BMW</strong> (iX1, iX2, iX3, i4, i5, i7, iX, 2 Series, 3 Series, 5 Series, 7 Series, X1, X2, X3, X5, XM, M5, i3, i8) with official <strong>price list equipment options</strong>, ADAC specifications, and verified engineering metrics.';
    }

    if (elements.btnCatalogLink) elements.btnCatalogLink.href = 'https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/bmw/';
    if (elements.btnCatalogLabel) elements.btnCatalogLabel.textContent = 'ADAC Catalog BMW Models';
    if (elements.btnExportCsvLabel) elements.btnExportCsvLabel.textContent = 'Export CSV (BMW Fleet)';
    if (elements.btnExportJsonLabel) elements.btnExportJsonLabel.textContent = 'Export JSON (BMW Fleet)';
    if (elements.btnExportMatching) elements.btnExportMatching.style.display = 'inline-flex';
    if (elements.btnExportPdf) elements.btnExportPdf.style.display = 'inline-flex';
    if (elements.btnExportPipelineCsv) elements.btnExportPipelineCsv.style.display = 'inline-flex';
    if (elements.bmwStudyFilterBar) elements.bmwStudyFilterBar.classList.remove('hidden');

    // KPIs
    if (elements.kpiTotalModels) elements.kpiTotalModels.textContent = '53';
    if (elements.kpiSubModels) elements.kpiSubModels.textContent = '100% of electrified BMW portfolio';
    if (elements.kpiLabelVolume) elements.kpiLabelVolume.textContent = 'Accounted BMW Fleet Deliveries';
    if (elements.kpiTotalVolume) elements.kpiTotalVolume.textContent = '574,883';
    if (elements.kpiSubVolume) elements.kpiSubVolume.textContent = 'Annual registrations across Europe & globally';
    if (elements.kpiPowertrainSplit) elements.kpiPowertrainSplit.textContent = '24 BEV / 29 PHEV';
    if (elements.kpiBevPct) elements.kpiBevPct.textContent = '45.3% Battery Electric (BEV) • 54.7% PHEV';
    if (elements.kpiLabelMetrics) elements.kpiLabelMetrics.textContent = 'Price Range & Top Power';
    if (elements.kpiAvgMetrics) elements.kpiAvgMetrics.textContent = '€79,250 Ø • Up to 748 hp';
    if (elements.kpiSubMetrics) elements.kpiSubMetrics.textContent = 'BMW base MSRP • Up to 1,000 Nm XM/M5';

    // Table Headers
    if (elements.thLabelSales) elements.thLabelSales.textContent = 'Registrations / Yr';
    if (elements.thLabelShare) elements.thLabelShare.textContent = 'BMW Fleet Share';
    if (elements.thLabelPrice) elements.thLabelPrice.textContent = 'Base Price (MSRP)';
    if (elements.thLabelRange) elements.thLabelRange.textContent = 'WLTP Range';
    if (elements.thLabelTowing) elements.thLabelTowing.textContent = 'Towing Capacity';
    if (elements.thLabelDc) elements.thLabelDc.textContent = 'Peak DC Fast Charge';
    if (elements.thLabelHighlights) elements.thLabelHighlights.textContent = 'Customer Study & Complaints';
    if (elements.thLabelActions) elements.thLabelActions.textContent = 'ADAC Catalog';

    if (elements.inputSearch) elements.inputSearch.placeholder = 'Search BMW model, series, or equipment (e.g. i4, M50, i5 Touring, 330e, 550e, X5 50e, XM, Curved Display, Bowers & Wilkins)...';

    // Sliders
    elements.rangeMaxPrice.max = 210000;
    elements.rangeMaxPrice.step = 5000;
    elements.rangeMaxPrice.value = 210000;
    elements.displayMaxPrice.textContent = 'No Limit';

    elements.rangeMinRange.max = 700;
    elements.rangeMinRange.step = 25;
    elements.rangeMinRange.value = 0;
    elements.displayMinRange.textContent = 'Any Range';

    // Methodology Card (BMW)
    if (elements.methodologyTitle) elements.methodologyTitle.textContent = 'BMW Fleet Census & Price List Methodology';
    if (elements.methodologyGrid) {
      elements.methodologyGrid.innerHTML = `
        <div class="methodology-item">
          <h4>1. 100% Full Census of All Electrified BMW Models</h4>
          <p>Captures every single series BEV and PHEV officially produced in Europe by BMW. Keine Lücken: von kompakten Ikonen wie <strong>i3</strong> und dem <strong>i8 Coupé/Roadster</strong> bis zu den modernsten Neuerscheinungen wie <strong>i5 Touring (G61)</strong>, <strong>X3 30e (G45)</strong>, <strong>X5 xDrive50e</strong>, <strong>M5 Limousine/Touring (727 PS)</strong> und <strong>XM Label Red (748 PS)</strong>.</p>
        </div>
        <div class="methodology-item">
          <h4>2. Official BMW Price Lists & Options Catalog</h4>
          <p>Comprehensive census of official price list equipment: <strong>BMW Curved Display</strong> (OS 8.5/9 mit QuickSelect), <strong>BMW Interaction Bar</strong>, <strong>Bowers & Wilkins Diamond Surround Sound</strong>, <strong>Hinterachsluftfederung</strong>, <strong>Towing Capacityen bis 2.700 kg</strong>, <strong>Wärmepumpe</strong> sowie <strong>IconicSounds Electric</strong> by Hans Zimmer.</p>
        </div>
        <div class="methodology-item">
          <h4>3. ADAC Autokatalog & Registration Volumes</h4>
          <p>Every vehicle links directly to official <strong>ADAC Autokatalog</strong>. Die Absatz- und Rangfolge basiert auf den offiziellen Auslieferungsstatistiken der BMW Group, den Neuzulassungen des Kraftfahrt-Bundesamtes (KBA) und ACEA-Marktberichten.</p>
        </div>
        <div class="methodology-item" style="grid-column: 1 / -1; border-top: 1px solid rgba(59, 130, 246, 0.25); padding-top: 1rem; margin-top: 0.5rem;">
          <h4 style="color:#60a5fa;display:flex;align-items:center;gap:6px;">
            <span>4. Customer Studies & Verified Complaint Matching</span>
            <span class="badge" style="background:rgba(16,185,129,0.15);color:#34d399;font-size:0.7rem;">✓ Strict ICE/F70 Exclusion</span>
          </h4>
          <p>Exact verification against internal customer study datasets (<strong>F70_G60_G68_G70_customer_studies.xlsx</strong> und den Hackathon-Feedbackdateien):
          Aus 13.771 Datensätzen wurden ausschließlich die 16 elektrifizierten Varianten <strong>G60 BEV (i5)</strong>, <strong>G60 PHEV (530e/550e)</strong>, <strong>G70 BEV (i7)</strong> und <strong>G70 PHEV (750e/M760e)</strong> gematcht. 
          <strong>F70 (1er) wurde zu 100% exkludiert</strong> (alle 4.076 Feedback-Einträge sind reine Verbrenner ohne EV/PHEV-Variante). Ebenso wurden alle <strong>5.724 ICE-Verbrennereinträge</strong> in G60 und G70 restlos herausgefiltert, um absolute Datenreinheit bei Beanstandungen zu garantieren.</p>
        </div>
      `;
    }
  }

  /**
   * Populate Brand / Series dropdown with unique counts
   */
  function populateBrandFilter() {
    if (currentMarket === 'BMW') {
      const modelCounts = {};
      allVehicles.forEach(v => {
        modelCounts[v.model] = (modelCounts[v.model] || 0) + 1;
      });

      const sortedModels = Object.keys(modelCounts).sort((a, b) => a.localeCompare(b));

      elements.selectBrand.innerHTML = `<option value="ALL">All BMW Series (${allVehicles.length} Modelle)</option>`;

      sortedModels.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m;
        opt.textContent = `BMW ${m} (${modelCounts[m]} Varianten)`;
        elements.selectBrand.appendChild(opt);
      });
      return;
    }

    const brandCounts = {};
    allVehicles.forEach(v => {
      brandCounts[v.brand] = (brandCounts[v.brand] || 0) + 1;
    });

    const sortedBrands = Object.keys(brandCounts).sort((a, b) => a.localeCompare(b, currentMarket === 'CN' ? 'zh-Hans-CN' : 'de-DE'));

    elements.selectBrand.innerHTML = `<option value="ALL">All Brands (${currentMarket === 'EU' ? 'Alle Marken' : '全部自主品牌'} - ${allVehicles.length})</option>`;

    sortedBrands.forEach(brand => {
      const opt = document.createElement('option');
      opt.value = brand;
      opt.textContent = `${brand} (${brandCounts[brand]})`;
      elements.selectBrand.appendChild(opt);
    });
  }

  /**
   * Filter and Sort Pipeline
   */
  function applyFiltersAndSort() {
    const query = filters.search.trim().toLowerCase();

    filteredVehicles = allVehicles.filter(car => {
      // Search
      if (query) {
        const brandEn = car.brand_en || '';
        const uspsText = Array.isArray(car.unique_selling_points) ? car.unique_selling_points.join(' ') : (car.unique_selling_points || '');
        const intText = Array.isArray(car.interior_highlights) ? car.interior_highlights.join(' ') : '';
        const extText = Array.isArray(car.exterior_highlights) ? car.exterior_highlights.join(' ') : '';
        const assText = Array.isArray(car.driver_assistance) ? car.driver_assistance.join(' ') : '';
        const ckpText = car.smart_cockpit || '';
        const adasText = car.autonomous_driving_system || '';
        const audioText = car.audio_system || '';

        const fullString = `${car.brand} ${brandEn} ${car.model} ${car.variant} ${car.body_type} ${car.powertrain} ${car.segment} ${ckpText} ${adasText} ${audioText} ${uspsText} ${intText} ${extText} ${assText}`.toLowerCase();
        
        const searchTerms = query.split(/\s+/);
        const matchesAllTerms = searchTerms.every(term => fullString.includes(term));
        if (!matchesAllTerms) return false;
      }

      // Powertrain
      if (filters.powertrain !== 'ALL') {
        if (filters.powertrain === 'BEV' && car.powertrain !== 'BEV') return false;
        if (filters.powertrain === 'PHEV' && !['PHEV', 'EREV'].includes(car.powertrain)) return false;
      }

      // Brand / Series
      if (filters.brand !== 'ALL') {
        if (currentMarket === 'BMW') {
          if (car.model !== filters.brand) return false;
        } else {
          if (car.brand !== filters.brand) return false;
        }
      }

      // Body Type
      if (filters.bodyType !== 'ALL') {
        const body = (car.body_type || '').toLowerCase();
        const target = filters.bodyType.toLowerCase();
        if (!body.includes(target) && !(target === 'kompakt' && body.includes('hatchback')) && !(target === 'limousine' && body.includes('sedan'))) {
          return false;
        }
      }

      // Drivetrain
      if (filters.drive !== 'ALL') {
        const drive = (car.drivetrain || '').toLowerCase();
        if (filters.drive === 'AWD' && !drive.includes('awd') && !drive.includes('四驱') && !drive.includes('all-wheel')) return false;
        if (filters.drive === 'RWD' && !drive.includes('rwd') && !drive.includes('后驱') && !drive.includes('rear')) return false;
        if (filters.drive === 'FWD' && !drive.includes('fwd') && !drive.includes('前驱') && !drive.includes('front')) return false;
      }

      // Towing capacity
      if (filters.towing > 0 && (car.towing_capacity_kg || 0) < filters.towing) {
        return false;
      }

      // Equipment / Preisliste Features
      if (filters.equipment === 'heatpump' && !['Serienmäßig', '标准全系高效宽温域热泵', '标准高效宽温域热泵'].includes(car.heat_pump)) {
        return false;
      }
      if (filters.equipment === 'frunk' && (!car.frunk_liters || car.frunk_liters <= 0)) {
        return false;
      }
      if (filters.equipment === 'fast18') {
        const chargeMin = car.charging_time_10_80_min || car.dc_charging_time_min || 30;
        if (chargeMin > 20) return false;
      }

      // Max Price
      if (car.base_price_eur > filters.maxPrice) {
        return false;
      }

      // Min Range
      const range = car.electric_range_wltp_km ?? car.electric_range_cltc_km ?? 0;
      if (range < filters.minRange) {
        return false;
      }

      // Customer Study Cohort Filter (Only in BMW mode)
      if (currentMarket === 'BMW' && filters.studyCohort !== 'ALL') {
        const isMatched = car.customer_study?.is_matched === true;
        if (filters.studyCohort === 'MATCHED' && !isMatched) return false;
        if (filters.studyCohort === 'UNSTUDIED' && isMatched) return false;
        if (filters.studyCohort === 'G60_BEV' && (car.customer_study?.match_cluster !== 'G60_BEV' && !['i5', 'i5 Touring'].includes(car.model))) return false;
        if (filters.studyCohort === 'G60_PHEV' && (car.customer_study?.match_cluster !== 'G60_PHEV' && !['5er', '5er Touring'].includes(car.model))) return false;
        if (filters.studyCohort === 'G70_BEV' && (car.customer_study?.match_cluster !== 'G70_BEV' && car.model !== 'i7')) return false;
        if (filters.studyCohort === 'G70_PHEV' && (car.customer_study?.match_cluster !== 'G70_PHEV' && car.model !== '7er')) return false;
      }

      return true;
    });

    // Sort
    sortVehicles(filteredVehicles, filters.sortKey, filters.sortDir);

    // Render Table
    renderTable();
  }

  /**
   * Sort array in-place
   */
  function sortVehicles(list, key, dir) {
    list.sort((a, b) => {
      let valA, valB;

      if (key === 'sales_units') {
        valA = a.europe_sales_units ?? a.china_sales_units ?? 0;
        valB = b.europe_sales_units ?? b.china_sales_units ?? 0;
      } else if (key === 'market_share_pct') {
        valA = a.europe_market_share_pct ?? a.china_market_share_pct ?? 0;
        valB = b.europe_market_share_pct ?? b.china_market_share_pct ?? 0;
      } else if (key === 'electric_range_km') {
        valA = a.electric_range_wltp_km ?? a.electric_range_cltc_km ?? 0;
        valB = b.electric_range_wltp_km ?? b.electric_range_cltc_km ?? 0;
      } else if (key === 'charging_speed') {
        valA = a.dc_charging_kw ?? (100 / (a.dc_charging_time_min || 30));
        valB = b.dc_charging_kw ?? (100 / (b.dc_charging_time_min || 30));
      } else {
        valA = a[key] ?? 0;
        valB = b[key] ?? 0;
      }

      if (typeof valA === 'string') {
        const comp = valA.localeCompare(valB, currentMarket === 'CN' ? 'zh-Hans-CN' : 'de-DE');
        return dir === 'asc' ? comp : -comp;
      }

      if (valA < valB) return dir === 'asc' ? -1 : 1;
      if (valA > valB) return dir === 'asc' ? 1 : -1;
      return 0;
    });
  }

  /**
   * Render vehicles to HTML table
   */
  function renderTable() {
    const count = filteredVehicles.length;
    const total = allVehicles.length;

    // Update Counts
    elements.searchCount.textContent = `Showing ${count} of ${total}`;
    elements.paginationInfo.textContent = `Showing 1 - ${count} of ${count} matching vehicles`;

    if (count === 0) {
      elements.tableBody.innerHTML = '';
      elements.emptyState.classList.remove('hidden');
      return;
    }

    elements.emptyState.classList.add('hidden');
    const fragment = document.createDocumentFragment();

    filteredVehicles.forEach(car => {
      const tr = document.createElement('tr');
      const isStudyMatched = currentMarket === 'BMW' && car.customer_study?.is_matched === true;
      tr.className = isStudyMatched ? 'vehicle-row row-study-matched' : 'vehicle-row';
      tr.setAttribute('data-id', car.rank);

      // Rank badge styling
      let rankClass = 'rank-pill';
      if (car.rank === 1) rankClass += ' rank-1';
      else if (car.rank === 2) rankClass += ' rank-2';
      else if (car.rank === 3) rankClass += ' rank-3';

      // Powertrain badge
      const isBev = car.powertrain === 'BEV';
      const ptBadge = isBev ? 'badge-bev' : 'badge-phev';

      // Top USP string
      let topUsp = '';
      if (Array.isArray(car.unique_selling_points) && car.unique_selling_points.length > 0) {
        topUsp = car.unique_selling_points[0];
      } else if (typeof car.unique_selling_points === 'string') {
        topUsp = car.unique_selling_points.split('|')[0].trim();
      }

      const salesUnits = car.europe_sales_units ?? car.china_sales_units ?? 0;
      const sharePct = (car.europe_market_share_pct ?? car.china_market_share_pct ?? 0).toFixed(2);
      const rangeKm = car.electric_range_wltp_km ?? car.electric_range_cltc_km ?? 0;
      const rangeLabel = currentMarket === 'CN' ? 'CLTC' : 'WLTP';

      // Price representation
      let priceHtml = '';
      if (currentMarket === 'CN') {
        priceHtml = `
          <strong class="text-emerald" style="font-size:0.95rem">${car.base_price_wan_rmb} 万元</strong>
          <small style="color:var(--text-muted);display:block;font-size:0.75rem">≈ ${formatCurrency(car.base_price_eur)}</small>
        `;
      } else {
        priceHtml = `<strong>${formatCurrency(car.base_price_eur)}</strong>`;
      }

      // Model display
      let modelHtml = '';
      if (currentMarket === 'CN') {
        modelHtml = `
          <div class="car-title">
            <strong>${escapeHtml(car.brand)} ${escapeHtml(car.model)}</strong>
            <span class="car-variant">${escapeHtml(car.brand_en || '')} • ${escapeHtml(car.variant)}</span>
          </div>
        `;
      } else if (currentMarket === 'BMW') {
        const study = car.customer_study;
        const studyPill = study && study.is_matched
          ? `<span class="badge" style="background:rgba(59, 130, 246, 0.15);color:#93c5fd;border:1px solid rgba(59, 130, 246, 0.3);font-size:0.68rem;padding:2px 6px;margin-top:3px;display:inline-flex;align-items:center;gap:3px;">✓ Study Matched</span>`
          : `<span class="badge" style="background:rgba(148, 163, 184, 0.08);color:#94a3b8;border:1px solid rgba(148, 163, 184, 0.18);font-size:0.68rem;padding:2px 6px;margin-top:3px;display:inline-flex;align-items:center;gap:3px;">⚪ Unstudied</span>`;
        modelHtml = `
          <div class="car-title">
            <strong>${escapeHtml(car.brand)} ${escapeHtml(car.model)}</strong>
            <span class="car-variant">${escapeHtml(car.variant)}</span>
            ${studyPill}
          </div>
        `;
      } else {
        modelHtml = `
          <div class="car-title">
            <strong>${escapeHtml(car.brand)} ${escapeHtml(car.model)}</strong>
            <span class="car-variant">${escapeHtml(car.variant)}</span>
          </div>
        `;
      }

      // Fast charge cell
      let chargeHtml = '';
      if (currentMarket === 'CN') {
        chargeHtml = `
          <span style="font-weight:600;color:var(--accent-cyan)">${car.charging_voltage || '400V'}</span>
          <small style="color:var(--text-muted);display:block;font-size:0.72rem">${car.dc_charging_time_min || 30} min</small>
        `;
      } else {
        chargeHtml = `
          <span>${car.dc_charging_kw > 0 ? car.dc_charging_kw + ' kW' : (car.charging_voltage || 'AC')}</span>
        `;
      }

      // Action link cell
      let actionHtml = '';
      if (currentMarket === 'CN') {
        actionHtml = `
          <a href="${escapeHtml(car.dongchedi_url)}" target="_blank" rel="noopener noreferrer" class="btn-adac-link" title="懂车帝 车型主页">
            <span>懂车帝</span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
          </a>
        `;
      } else {
        actionHtml = `
          <a href="${escapeHtml(car.adac_url)}" target="_blank" rel="noopener noreferrer" class="btn-adac-link" title="Open ADAC Autokatalog entry">
            <span>ADAC</span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
          </a>
        `;
      }

      // Highlights / Customer Study Cell
      let highlightsHtml = '';
      if (currentMarket === 'BMW') {
        const study = car.customer_study;
        if (study && study.is_matched) {
          const topTopic = study.top_complaint_categories && study.top_complaint_categories[0]
            ? study.top_complaint_categories[0]
            : { topic: 'Allgemein', count: 0 };
          highlightsHtml = `
            <div class="study-cell-info">
              <div class="study-cell-pill">
                <span class="study-badge-tag">${escapeHtml(study.cohort_name)}</span>
                <span class="study-score-tag">⭐ ${study.satisfaction_scores.overall_eu} / 10</span>
              </div>
              <div class="study-cell-stats">
                <span class="text-amber" style="font-weight:600;">⚠️ ${study.complaints_count} Beanstandungen (${study.complaint_ratio_pct}%)</span>
                <span class="study-top-cat">Top: <strong>${escapeHtml(topTopic.topic)}</strong> (${topTopic.count})</span>
              </div>
            </div>
          `;
        } else {
          highlightsHtml = `
            <div class="study-cell-info">
              <span class="study-unstudied-tag">⚪ Nicht in Kohortenstudie</span>
              <small style="color:var(--text-muted);display:block;font-size:0.75rem;margin-top:2px;">100% ICE & andere Baureihen exkludiert</small>
            </div>
          `;
        }
      } else {
        highlightsHtml = `
          <span class="highlight-chip highlight-chip-usp" title="${escapeHtml(topUsp)}">
            ★ ${escapeHtml(topUsp)}
          </span>
        `;
      }

      tr.innerHTML = `
        <td class="col-rank">
          <span class="${rankClass}">${car.rank}</span>
        </td>
        <td class="col-car">
          ${modelHtml}
        </td>
        <td class="col-powertrain">
          <span class="badge ${ptBadge}">${car.powertrain}</span>
        </td>
        <td class="col-sales">
          <strong class="text-cyan">${formatNumber(salesUnits)}</strong>
        </td>
        <td class="col-share">
          <span>${sharePct}%</span>
        </td>
        <td class="col-price">
          ${priceHtml}
        </td>
        <td class="col-range">
          <span class="range-value">${rangeKm > 0 ? rangeKm + ' km' : '-'}</span>
          <small style="color:var(--text-muted);display:block;font-size:0.72rem">${rangeLabel}</small>
        </td>
        <td class="col-battery">
          <span>${car.battery_capacity_kwh > 0 ? car.battery_capacity_kwh.toFixed(1) + ' kWh' : '-'}</span>
        </td>
        <td class="col-power">
          <span>${car.power_ps} PS <small style="color:var(--text-muted)">(${car.power_kw} kW)</small></span>
        </td>
        <td class="col-drive">
          <span class="badge badge-dark">${car.drivetrain}</span>
        </td>
        <td class="col-towing">
          <span style="font-weight:600">${car.towing_capacity_kg > 0 ? formatNumber(car.towing_capacity_kg) + ' kg' : '—'}</span>
        </td>
        <td class="col-dc">
          ${chargeHtml}
        </td>
        <td class="col-charge">
          <span style="font-size:0.85rem">${(car.charging_time_10_80_min || car.dc_charging_time_min) > 0 ? (car.charging_time_10_80_min || car.dc_charging_time_min) + ' min' : '—'}</span>
        </td>
        <td class="col-highlights">
          ${highlightsHtml}
        </td>
        <td class="col-actions">
          ${actionHtml}
        </td>
      `;

      // Open Modal on row click
      tr.addEventListener('click', e => {
        if (e.target.closest('.btn-adac-link')) return;
        openModal(car);
      });

      fragment.appendChild(tr);
    });

    elements.tableBody.innerHTML = '';
    elements.tableBody.appendChild(fragment);
  }

  /**
   * Modal Dialog Display
   */
  function openModal(car) {
    // Header
    elements.modalRankBadge.textContent = `#${car.rank}`;
    elements.modalTypeBadge.textContent = car.powertrain;
    elements.modalTypeBadge.className = car.powertrain === 'BEV' ? 'badge badge-bev' : 'badge badge-phev';
    elements.modalSegmentBadge.textContent = `${car.segment} • ${car.body_type}`;

    if (currentMarket === 'CN') {
      elements.modalTitle.textContent = `${car.brand} ${car.model}`;
      elements.modalVariant.textContent = `${car.brand_en || ''} ${car.variant} (${car.drivetrain}) • ${car.charging_voltage || '400V'}`;
    } else {
      elements.modalTitle.textContent = `${car.brand} ${car.model}`;
      elements.modalVariant.textContent = `${car.variant} (${car.drivetrain})`;
    }

    // USPs list
    const uspsArray = Array.isArray(car.unique_selling_points) ? car.unique_selling_points : (car.unique_selling_points ? car.unique_selling_points.split('|') : []);
    elements.modalUspsList.innerHTML = uspsArray.map(item => `
      <div class="feature-item">
        <div class="feature-icon">★</div>
        <div class="feature-text"><strong>${escapeHtml(item.trim())}</strong></div>
      </div>
    `).join('');

    // Tab 2: Interior List
    const interiorArray = Array.isArray(car.interior_highlights) ? car.interior_highlights : (car.interior_highlights ? car.interior_highlights.split('|') : []);
    elements.modalInteriorList.innerHTML = interiorArray.map(item => `
      <div class="feature-item">
        <div class="feature-icon">🛋️</div>
        <div class="feature-text">${escapeHtml(item.trim())}</div>
      </div>
    `).join('');

    // Tab 3: Exterior List
    const exteriorArray = Array.isArray(car.exterior_highlights) ? car.exterior_highlights : (car.exterior_highlights ? car.exterior_highlights.split('|') : []);
    elements.modalExteriorList.innerHTML = exteriorArray.map(item => `
      <div class="feature-item">
        <div class="feature-icon">🏎️</div>
        <div class="feature-text">${escapeHtml(item.trim())}</div>
      </div>
    `).join('');

    // Tab 4: Assistance List
    const assistanceArray = Array.isArray(car.driver_assistance) ? car.driver_assistance : (car.driver_assistance ? car.driver_assistance.split('|') : []);
    elements.modalAssistanceList.innerHTML = assistanceArray.map(item => `
      <div class="feature-item">
        <div class="feature-icon">🛡️</div>
        <div class="feature-text">${escapeHtml(item.trim())}</div>
      </div>
    `).join('');

    // Tab 5: Practicality
    elements.modalTowing.textContent = car.towing_capacity_kg > 0 ? `${formatNumber(car.towing_capacity_kg)} kg gebremst` : 'Keine Towing Capacity freigegeben';
    elements.modalFrunk.textContent = car.frunk_liters > 0 ? `${car.frunk_liters} Liter` : 'Kein Frunk vorhanden';
    elements.modalTrunk.textContent = car.trunk_liters || '—';
    elements.modalHeatpump.textContent = car.heat_pump || 'Optional';
    const chargeMin = car.charging_time_10_80_min || car.dc_charging_time_min;
    elements.modalChargeTime.textContent = chargeMin > 0 ? `${chargeMin} Minuten (10-80%)` : 'N/A';
    elements.modalHud.textContent = car.head_up_display || 'N/A';
    elements.modalAudio.textContent = car.audio_system || 'Standard Soundsystem';

    // Tab 6: Tech Specs
    const salesVolume = car.europe_sales_units ?? car.china_sales_units ?? 0;
    const shareVal = car.europe_market_share_pct ?? car.china_market_share_pct ?? 0;
    elements.modalSales.textContent = `${formatNumber(salesVolume)} units / year`;
    elements.modalShare.textContent = `${shareVal.toFixed(2)}% Market Share`;

    if (currentMarket === 'CN') {
      elements.modalPrice.textContent = `${car.base_price_wan_rmb} 万元 (≈ ${formatCurrency(car.base_price_eur)})`;
      elements.modalRange.textContent = `${car.electric_range_cltc_km} km (CLTC)`;
    } else {
      elements.modalPrice.textContent = formatCurrency(car.base_price_eur);
      elements.modalRange.textContent = `${car.electric_range_wltp_km} km (WLTP)`;
    }

    elements.modalBattery.textContent = car.battery_capacity_kwh > 0 ? `${car.battery_capacity_kwh} kWh (${car.battery_type || 'Net'})` : 'N/A';
    elements.modalPower.textContent = `${car.power_kw} kW (${car.power_ps} PS)`;
    elements.modalDrive.textContent = `${car.drivetrain}`;
    elements.modalDc.textContent = car.charging_voltage ? `${car.charging_voltage} 高压架构 (${chargeMin} min)` : (car.dc_charging_kw > 0 ? `${car.dc_charging_kw} kW Peak` : 'AC only');
    elements.modalAccel.textContent = car.accel_0_100_s ? `${car.accel_0_100_s.toFixed(1)} s` : '-';
    elements.modalTopSpeed.textContent = car.top_speed_kmh ? `${car.top_speed_kmh} km/h` : '-';
    elements.modalEfficiency.textContent = car.efficiency || '-';
    elements.modalBodyType.textContent = `${car.body_type} (${car.segment})`;

    elements.modalEvidence.textContent = `${car.sales_evidence_source || car.evidence_source || ''}`;

    // Modal Footer Links
    if (currentMarket === 'CN') {
      elements.modalFooterContainer.className = 'modal-footer modal-footer-dual';
      elements.modalFooterContainer.innerHTML = `
        <a href="${escapeHtml(car.dongchedi_url)}" target="_blank" rel="noopener noreferrer" class="btn btn-dongchedi" style="text-align:center;justify-content:center;">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
          懂车帝 Dongchedi 车型主页
        </a>
        <a href="${escapeHtml(car.autohome_url)}" target="_blank" rel="noopener noreferrer" class="btn btn-autohome" style="text-align:center;justify-content:center;">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
          汽车之家 Autohome 参数配置
        </a>
      `;
    } else {
      elements.modalFooterContainer.className = 'modal-footer';
      elements.modalFooterContainer.innerHTML = `
        <a id="modal-adac-link" href="${escapeHtml(car.adac_url)}" target="_blank" rel="noopener noreferrer" class="btn btn-primary full-width">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
          View Full Model on ADAC Autokatalog
        </a>
      `;
    }

    // Tab 7: Customer Study & Complaints (BMW Fleet or if customer_study available)
    if (elements.modalFeedbackBtn && elements.modalFeedbackContent) {
      if (currentMarket === 'BMW' || car.customer_study) {
        elements.modalFeedbackBtn.style.display = 'inline-flex';
        const study = car.customer_study;
        if (study && study.is_matched) {
          elements.modalFeedbackBtn.textContent = '💬 Customer Complaints (Matched)';
          elements.modalFeedbackBtn.classList.add('tab-highlight');

          const topComplaintsHtml = (study.top_complaint_categories || []).map(c => {
            const maxVal = study.top_complaint_categories[0] ? study.top_complaint_categories[0].count : 1;
            const pct = Math.min(100, Math.round((c.count / maxVal) * 100));
            return `
              <div class="complaint-item">
                <div class="complaint-item-top">
                  <span class="complaint-topic-name">${escapeHtml(c.topic)}</span>
                  <span class="complaint-topic-count">${c.count} Beanstandungen</span>
                </div>
                <div class="complaint-desc">${escapeHtml(c.detail)}</div>
                <div class="complaint-bar-bg">
                  <div class="complaint-bar-val" style="width: ${pct}%"></div>
                </div>
              </div>
            `;
          }).join('');

          const scores = study.satisfaction_scores || {};
          const scoresHtml = Object.entries(scores).map(([k, v]) => {
            const cleanKey = k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            const scoreColor = v >= 9.0 ? 'text-emerald' : (v >= 8.0 ? 'text-cyan' : (v < 7.5 ? 'text-amber' : ''));
            return `
              <div class="sat-score-row">
                <span class="sat-score-lbl">${escapeHtml(cleanKey)}</span>
                <strong class="sat-score-num ${scoreColor}">${Number(v).toFixed(2)} / 10</strong>
              </div>
            `;
          }).join('');

          elements.modalFeedbackContent.innerHTML = `
            <div class="feedback-container">
              <div class="feedback-banner">
                <div class="feedback-banner-header">
                  <span class="feedback-banner-title">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                    Verifizierte Kohorte: ${escapeHtml(study.cohort_name)}
                  </span>
                  <span class="feedback-badge-strict">✓ ICE & F70 100% Excluded</span>
                </div>
                <p class="feedback-banner-desc">
                  Datenabgleich mit <strong>F70_G60_G68_G70_customer_studies.xlsx</strong> und <strong>${escapeHtml(study.derivate.split(' ')[0])}_feedback_hackathon.xlsx</strong>.
                  Streng gefiltert auf <code>Engine Type == '${escapeHtml(study.engine_type)}'</code>. Reines Verbrenner-Feedback (ICE) und F70 wurden vollständig ausgeschlossen.
                </p>
              </div>

              <div class="feedback-kpi-grid">
                <div class="feedback-kpi-card">
                  <span class="feedback-kpi-val text-cyan">${formatNumber(study.surveyed_records)}</span>
                  <span class="feedback-kpi-lbl">Feedback Records</span>
                </div>
                <div class="feedback-kpi-card">
                  <span class="feedback-kpi-val text-amber">${study.complaints_count}</span>
                  <span class="feedback-kpi-lbl">Beanstandungen</span>
                </div>
                <div class="feedback-kpi-card">
                  <span class="feedback-kpi-val text-emerald">${study.likes_count}</span>
                  <span class="feedback-kpi-lbl">Positive Feedbacks</span>
                </div>
                <div class="feedback-kpi-card">
                  <span class="feedback-kpi-val text-cyan">${study.satisfaction_scores.overall_eu} ★</span>
                  <span class="feedback-kpi-lbl">EU Zufriedenheit</span>
                </div>
              </div>

              <div>
                <h4 class="feedback-section-title">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                  Häufigste Beanstandungsbereiche (${escapeHtml(study.engine_type)}):
                </h4>
                <div class="complaint-list">
                  ${topComplaintsHtml}
                </div>
              </div>

              <div>
                <h4 class="feedback-section-title">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2"><path d="M12 20v-6M6 20V10M18 20V4"/></svg>
                  Empirische Zufriedenheitswerte (Customer Study CN_EU_2025):
                </h4>
                <div class="satisfaction-scores-grid">
                  ${scoresHtml}
                </div>
              </div>
            </div>
          `;
        } else {
          elements.modalFeedbackBtn.textContent = '💬 Customer Study (Unstudied)';
          elements.modalFeedbackBtn.classList.remove('tab-highlight');
          elements.modalFeedbackContent.innerHTML = `
            <div class="unstudied-notice-box">
              <svg width="42" height="42" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
              <h4 class="unstudied-notice-title">Modell nicht in F70/G60/G70 Kohortenstudie</h4>
              <p class="unstudied-notice-text">
                Dieses elektrifizierte BMW-Modell (<strong>${escapeHtml(car.brand)} ${escapeHtml(car.model)} ${escapeHtml(car.variant)}</strong>) gehört zu einer eigenständigen Baureihe (z.B. iX1, i4, iX, 330e, X5 50e), die in der vorliegenden Feedback-Stichprobe nicht erfasst wurde.
              </p>
              <p class="unstudied-notice-text" style="color:var(--accent-cyan);font-size:0.8rem">
                ✓ <strong>Strikte Validierungsregel:</strong> Um fehlerhafte Zuordnungen auszuschließen, wurden ausschließlich die echten G60- (i5/5er) und G70-Modelle (i7/7er) mit BEVE/PHEV-Filter gematcht. F70 (100% ICE) und G60/G70-Verbrenner wurden exkludiert.
              </p>
            </div>
          `;
        }
      } else {
        elements.modalFeedbackBtn.style.display = 'none';
      }
    }

    // Reset active tab to 'usps'
    switchTab('usps');

    elements.modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }

  function switchTab(tabId) {
    elements.modalTabs.forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-tab') === tabId);
    });

    elements.modalTabPanes.forEach(pane => {
      pane.classList.toggle('active', pane.id === `tab-pane-${tabId}`);
    });
  }

  function closeModal() {
    elements.modal.classList.add('hidden');
    document.body.style.overflow = '';
  }

  /**
   * Reset All Filters to Defaults
   */
  function resetFilters() {
    filters.search = '';
    filters.powertrain = 'ALL';
    filters.brand = 'ALL';
    filters.bodyType = 'ALL';
    filters.drive = 'ALL';
    filters.towing = 0;
    filters.equipment = 'ALL';
    filters.maxPrice = currentMarket === 'CN' ? 200000 : (currentMarket === 'BMW' ? 210000 : 300000);
    filters.minRange = 0;
    filters.sortKey = 'rank';
    filters.sortDir = 'asc';

    if (elements.inputSearch) elements.inputSearch.value = '';
    if (elements.selectBrand) elements.selectBrand.value = 'ALL';
    if (elements.selectBody) elements.selectBody.value = 'ALL';
    if (elements.selectDrive) elements.selectDrive.value = 'ALL';
    if (elements.selectTowing) elements.selectTowing.value = '0';
    if (elements.selectEquipment) elements.selectEquipment.value = 'ALL';
    if (elements.selectSort) elements.selectSort.value = 'rank-asc';

    elements.powertrainPills.forEach(b => {
      b.classList.toggle('active', b.getAttribute('data-filter-powertrain') === 'ALL');
    });

    elements.rangeMaxPrice.value = filters.maxPrice;
    elements.displayMaxPrice.textContent = 'No Limit';
    elements.rangeMinRange.value = 0;
    elements.displayMinRange.textContent = 'Any Range';

    filters.studyCohort = 'ALL';
    if (elements.studyChips) {
      elements.studyChips.forEach(c => c.classList.toggle('active', c.getAttribute('data-study-filter') === 'ALL'));
    }

    updateSortHeaderStyles();
    populateBrandFilter();
    applyFiltersAndSort();
  }

  /**
   * Update Sort indicators in Table Headers
   */
  function updateSortHeaderStyles() {
    elements.sortableHeaders.forEach(th => {
      const key = th.getAttribute('data-sort-key');
      th.classList.remove('sort-asc', 'sort-desc');
      if (key === filters.sortKey) {
        th.classList.add(filters.sortDir === 'asc' ? 'sort-asc' : 'sort-desc');
      }
    });
  }

  /**
   * Export Dataset to CSV
   */
  function exportCsv() {
    let filename = 'top_500_ev_phev_europe.csv';
    if (currentMarket === 'CN') filename = 'top_500_china_nev.csv';
    else if (currentMarket === 'BMW') filename = 'bmw_ev_phev_catalog.csv';

    const link = document.createElement('a');
    link.href = filename;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  /**
   * Export Dataset to JSON
   */
  function exportJson() {
    let filename = 'top_500_ev_phev_europe.json';
    if (currentMarket === 'CN') filename = 'top_500_china_nev.json';
    else if (currentMarket === 'BMW') filename = 'bmw_ev_phev_catalog.json';

    const link = document.createElement('a');
    link.href = filename;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  /**
   * Export BMW Matching & Complaints CSV
   */
  function exportMatchingCsv() {
    const filename = 'bmw_ev_complaint_matching.csv';
    const link = document.createElement('a');
    link.href = filename;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  /**
   * Helper: Escape HTML
   */
  function escapeHtml(str) {
    if (typeof str !== 'string') return str;
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  /**
   * Event Listeners Registration
   */
  function bindEventListeners() {
    // Market Selectors
    if (elements.marketToggleEu) {
      elements.marketToggleEu.addEventListener('click', () => setMarket('EU'));
    }
    if (elements.marketToggleCn) {
      elements.marketToggleCn.addEventListener('click', () => setMarket('CN'));
    }
    if (elements.marketToggleBmw) {
      elements.marketToggleBmw.addEventListener('click', () => setMarket('BMW'));
    }

    // Search input (debounced)
    let searchTimeout;
    elements.inputSearch.addEventListener('input', e => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        filters.search = e.target.value;
        applyFiltersAndSort();
      }, 150);
    });

    // Powertrain pills
    elements.powertrainPills.forEach(btn => {
      btn.addEventListener('click', () => {
        elements.powertrainPills.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        filters.powertrain = btn.getAttribute('data-filter-powertrain');
        applyFiltersAndSort();
      });
    });

    // Brand filter
    elements.selectBrand.addEventListener('change', e => {
      filters.brand = e.target.value;
      applyFiltersAndSort();
    });

    // Body type filter
    elements.selectBody.addEventListener('change', e => {
      filters.bodyType = e.target.value;
      applyFiltersAndSort();
    });

    // Drivetrain filter
    elements.selectDrive.addEventListener('change', e => {
      filters.drive = e.target.value;
      applyFiltersAndSort();
    });

    // Towing filter
    if (elements.selectTowing) {
      elements.selectTowing.addEventListener('change', e => {
        filters.towing = parseInt(e.target.value, 10) || 0;
        applyFiltersAndSort();
      });
    }

    // Equipment filter
    if (elements.selectEquipment) {
      elements.selectEquipment.addEventListener('change', e => {
        filters.equipment = e.target.value;
        applyFiltersAndSort();
      });
    }

    // Sort dropdown
    elements.selectSort.addEventListener('change', e => {
      const [key, dir] = e.target.value.split('-');
      if (key === 'sales') filters.sortKey = 'sales_units';
      else if (key === 'price') filters.sortKey = 'base_price_eur';
      else if (key === 'range') filters.sortKey = 'electric_range_km';
      else if (key === 'power') filters.sortKey = 'power_ps';
      else if (key === 'dc') filters.sortKey = 'charging_speed';
      else if (key === 'accel') filters.sortKey = 'accel_0_100_s';
      else if (key === 'towing') filters.sortKey = 'towing_capacity_kg';
      else filters.sortKey = 'rank';

      filters.sortDir = dir;
      updateSortHeaderStyles();
      applyFiltersAndSort();
    });

    // Table Header Sort clicks
    elements.sortableHeaders.forEach(th => {
      th.addEventListener('click', () => {
        const key = th.getAttribute('data-sort-key');
        if (filters.sortKey === key) {
          filters.sortDir = filters.sortDir === 'asc' ? 'desc' : 'asc';
        } else {
          filters.sortKey = key;
          filters.sortDir = (key === 'rank' || key === 'base_price_eur' || key === 'accel_0_100_s' || key === 'model') ? 'asc' : 'desc';
        }
        updateSortHeaderStyles();
        applyFiltersAndSort();
      });
    });

    // Sliders
    elements.rangeMaxPrice.addEventListener('input', e => {
      const val = parseInt(e.target.value, 10);
      filters.maxPrice = val;
      elements.displayMaxPrice.textContent = val >= elements.rangeMaxPrice.max ? 'No Limit' : `${formatCurrency(val)}`;
      applyFiltersAndSort();
    });

    elements.rangeMinRange.addEventListener('input', e => {
      const val = parseInt(e.target.value, 10);
      filters.minRange = val;
      elements.displayMinRange.textContent = val === 0 ? 'Any Range' : `${val}+ km`;
      applyFiltersAndSort();
    });

    // Reset Buttons
    elements.btnReset.addEventListener('click', resetFilters);
    elements.btnEmptyReset.addEventListener('click', resetFilters);

    // Export Buttons
    elements.btnExportCsv.addEventListener('click', exportCsv);
    elements.btnExportJson.addEventListener('click', exportJson);
    if (elements.btnExportMatching) elements.btnExportMatching.addEventListener('click', exportMatchingCsv);

    // Study Filter Chips (BMW mode)
    if (elements.studyChips) {
      elements.studyChips.forEach(chip => {
        chip.addEventListener('click', () => {
          elements.studyChips.forEach(c => c.classList.remove('active'));
          chip.classList.add('active');
          filters.studyCohort = chip.getAttribute('data-study-filter');
          applyFiltersAndSort();
        });
      });
    }

    // Modal Tabs
    elements.modalTabs.forEach(tabBtn => {
      tabBtn.addEventListener('click', () => {
        const targetTab = tabBtn.getAttribute('data-tab');
        switchTab(targetTab);
      });
    });

    // Modal close
    elements.modalCloseBtn.addEventListener('click', closeModal);
    elements.modal.addEventListener('click', e => {
      if (e.target === elements.modal) closeModal();
    });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && !elements.modal.classList.contains('hidden')) {
        closeModal();
      }
    });
  }

  // Start app on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
