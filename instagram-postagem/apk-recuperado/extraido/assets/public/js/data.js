// ============================================================
// DADOS DE EXEMPLO — Painel Pata3D
// Este é o ÚNICO arquivo que muda quando ligarmos no motor real.
// Hoje: dados fixos de exemplo. Amanhã: trocar por fetch() do backend Python.
// ============================================================

const DB = {
  // ---- CONTAS ----
  // cor = identidade fixa da conta (aparece em toda tela)
  // token: { estado: 'ok'|'expirando'|'morto', diasRestantes }
  contas: [
    {
      id: "cortadores",
      nome: "Pata3D Cortadores",
      rede: "instagram",
      cor: "#8B7CF6",
      tema: "Cortadores 3D artesanais",
      automatico: true,
      token: { estado: "ok", diasRestantes: 58 },
      estoqueDias: 11,
    },
    {
      id: "artesanato",
      nome: "Pata3D Artesanato",
      rede: "instagram",
      cor: "#3FB984",
      tema: "Peças artesanais e decoração",
      automatico: true,
      token: { estado: "expirando", diasRestantes: 5 },
      estoqueDias: 2,
    },
    {
      id: "produtos",
      nome: "Pata3D Produtos",
      rede: "instagram",
      cor: "#E0693A",
      tema: "Produtos reais da loja",
      automatico: false,
      token: { estado: "ok", diasRestantes: 42 },
      estoqueDias: 18,
    },
    {
      id: "x",
      nome: "Pata3D no X",
      rede: "x",
      cor: "#9AA0A6",
      tema: "Novidades e bastidores",
      automatico: true,
      token: { estado: "ok", diasRestantes: 90 },
      estoqueDias: 25,
    },
  ],

  // ---- PENDÊNCIAS (aparecem na aba Hoje) ----
  pendencias: [
    { contaId: "artesanato", tipo: "token", texto: "Token vence em 5 dias", acao: "Renovar" },
    { contaId: "cortadores", tipo: "aprovar", texto: "2 posts esperando aprovação", acao: "Ver" },
    { contaId: "artesanato", tipo: "estoque", texto: "Estoque acabando: 2 dias", acao: "Abastecer" },
  ],

  // ---- PRÓXIMOS POSTS (aba Hoje) ----
  proximos: [
    { hora: "14:00", contaId: "cortadores", formato: "reel", status: "aprovar", titulo: "Reel do cortador de coração", img: "img/p1.jpg" },
    { hora: "14:20", contaId: "produtos", formato: "feed", status: "agendado", titulo: "Vaso decorativo azul", img: "img/p2.jpg" },
    { hora: "15:00", contaId: "x", formato: "x", status: "agendado", titulo: "Novidade da semana", img: "img/p3.jpg" },
    { hora: "16:30", contaId: "cortadores", formato: "story", status: "agendado", titulo: "Bastidores da impressão", img: "img/p4.jpg" },
    { hora: "11:30", contaId: "artesanato", formato: "story", status: "publicado", titulo: "Peça finalizada", img: "img/p5.jpg" },
  ],

  // ---- RESUMO DO DIA (aba Hoje, cartão de topo) ----
  resumoHoje: {
    tudoOk: true,
    contasAtivas: 3,
    postsHoje: 12,
  },

  // ---- AGENDA (grade: por conta, posts por dia da semana) ----
  // dias: [seg, ter, qua, qui, sex, sab, dom]
  agenda: {
    semana: "13 a 19 out",
    linhas: [
      { contaId: "cortadores", dias: [6, 6, 6, 6, 6, 4, 4] },
      { contaId: "artesanato", dias: [5, 5, 0, 0, 0, 0, 0] }, // zera na quarta = alerta
      { contaId: "produtos", dias: [3, 3, 3, 3, 3, 2, 2] },
      { contaId: "x", dias: [4, 4, 4, 4, 4, 3, 3] },
    ],
    // detalhe de um dia selecionado (exemplo: segunda, cortadores)
    detalhe: {
      titulo: "Segunda, 13 · Cortadores",
      posts: [
        { hora: "09:10", formato: "story", status: "agendado", img: "img/p16.jpg" },
        { hora: "10:05", formato: "feed", status: "aprovar", img: "img/p17.jpg" },
        { hora: "12:40", formato: "reel", status: "agendado", img: "img/p18.jpg" },
        { hora: "18:30", formato: "carrossel", status: "agendado", img: "img/p19.jpg" },
      ],
    },
  },

  // ---- ESTOQUE (aba Estoque) ----
  // cada conta: quantos itens prontos por formato
  estoque: [
    { contaId: "cortadores", fotos: 16, videos: 4, dias: 11, capas: ["img/p9.jpg", "img/p10.jpg", "img/p11.jpg"] },
    { contaId: "artesanato", fotos: 0, videos: 0, dias: 2, capas: [] },
    { contaId: "produtos", fotos: 22, videos: 2, dias: 18, capas: ["img/p12.jpg", "img/p13.jpg", "img/p14.jpg"] },
    { contaId: "x", fotos: 30, videos: 0, dias: 25, capas: ["img/p15.jpg", "img/p20.jpg", "img/p6.jpg"] },
  ],

  // ---- DESEMPENHO (aba Desempenho) ----
  desempenho: {
    // alcance por dia (últimos 7 dias) por conta
    alcance: {
      labels: ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"],
      cortadores: [820, 1100, 980, 1340, 1620, 1480, 1710],
      artesanato: [410, 520, 480, 300, 180, 0, 0], // caiu (sem estoque)
    },
    volumeAtual: { postsSemana: 78, tendencia: "subindo" },
    melhores: [
      { contaId: "cortadores", titulo: "Reel coração 3D", alcance: 4820, formato: "reel", img: "img/p6.jpg" },
      { contaId: "produtos", titulo: "Carrossel vasos", alcance: 3110, formato: "carrossel", img: "img/p7.jpg" },
      { contaId: "cortadores", titulo: "Antes e depois", alcance: 2740, formato: "feed", img: "img/p8.jpg" },
    ],
  },
};

// ---- CATÁLOGO SEMANAL (colunas Seg..Dom, cards com foto grande) ----
DB.catalogoSemana = {
  semana: "13 a 19 out",
  dias: [
    { nome: "Seg", data: "13", posts: [
      { contaId: "cortadores", formato: "feed", hora: "14:00", status: "aprovar", titulo: "Cortador coração", img: "img/p1.jpg" },
      { contaId: "cortadores", formato: "reel", hora: "18:30", status: "pronto", titulo: "Bastidores", img: "img/p12.jpg" },
      { contaId: "produtos", formato: "feed", hora: "20:00", status: "pronto", titulo: "Vaso azul", img: "img/p2.jpg" },
    ]},
    { nome: "Ter", data: "14", posts: [
      { contaId: "produtos", formato: "feed", hora: "14:00", status: "editar", titulo: "Kit confeitaria", img: "img/p13.jpg" },
      { contaId: "x", formato: "x", hora: "16:00", status: "editar", titulo: "Novidade", img: "img/p3.jpg" },
      { contaId: "cortadores", formato: "reel", hora: "19:00", status: "aprovar", titulo: "Antes e depois", img: "img/p8.jpg" },
    ]},
    { nome: "Qua", data: "15", posts: [
      { contaId: "cortadores", formato: "feed", hora: "14:00", status: "pronto", titulo: "Coleção nova", img: "img/p9.jpg" },
      { contaId: "cortadores", formato: "reel", hora: "18:00", status: "analise", titulo: "Processo 3D", img: "img/p10.jpg" },
    ]},
    { nome: "Qui", data: "16", posts: [
      { contaId: "cortadores", formato: "feed", hora: "14:00", status: "aprovar", titulo: "Cortador gato", img: "img/p11.jpg" },
      { contaId: "produtos", formato: "feed", hora: "17:00", status: "editar", titulo: "Flor de resina", img: "img/p14.jpg" },
      { contaId: "artesanato", formato: "feed", hora: "20:00", status: "aprovar", titulo: "Peça pintada", img: "img/p7.jpg" },
    ]},
    { nome: "Sex", data: "17", posts: [
      { contaId: "x", formato: "x", hora: "14:00", status: "editar", titulo: "Promo sexta", img: "img/p15.jpg" },
      { contaId: "cortadores", formato: "reel", hora: "19:00", status: "editar", titulo: "Unboxing", img: "img/p4.jpg" },
    ]},
    { nome: "Sáb", data: "18", posts: [
      { contaId: "produtos", formato: "feed", hora: "11:00", status: "editar", titulo: "Vitrine", img: "img/p20.jpg" },
      { contaId: "cortadores", formato: "reel", hora: "16:00", status: "editar", titulo: "Dica rápida", img: "img/p18.jpg" },
    ]},
    { nome: "Dom", data: "19", posts: [
      { contaId: "cortadores", formato: "reel", hora: "16:00", status: "editar", titulo: "Resumo semana", img: "img/p16.jpg" },
      { contaId: "produtos", formato: "feed", hora: "19:00", status: "pronto", titulo: "Lançamento", img: "img/p17.jpg" },
    ]},
  ],
};

// ---- GRADE DE CANAIS (contas x dias, estilo programação de TV) ----
DB.grade = {
  dias: ["SEGUNDA", "TERÇA", "QUARTA", "QUINTA", "SEXTA"],
  canais: [
    { nome: "Pata3D", plataforma: "Instagram", cor: "#8b5cf6", posts: [
      { k: "FEED", t: "Novidade da semana", hora: "10:30", img: "img/p2.jpg" },
      { k: "REEL", t: "Cortador coração", hora: "12:00", img: "img/p1.jpg" },
      { k: "FEED", t: "Coleção nova", hora: "11:15", img: "img/p9.jpg" },
      { k: "STORY", t: "Bastidores 3D", hora: "18:30", img: "img/p12.jpg" },
      { k: "REEL", t: "Antes e depois", hora: "19:00", img: "img/p8.jpg" },
    ]},
    { nome: "Estátua", plataforma: "Instagram", cor: "#ec4899", posts: [
      { k: "FEED", t: "Estátua PVC nova", hora: "11:15", img: "img/p6.jpg" },
      { k: "REEL", t: "Processo de pintura", hora: "16:00", img: "img/p7.jpg" },
      { k: "FEED", t: "Detalhe da peça", hora: "14:20", img: "img/p14.jpg" },
      { k: "STORY", t: "Enquete da semana", hora: "10:00", img: "img/p10.jpg" },
      { k: "FEED", t: "Peça finalizada", hora: "20:00", img: "img/p17.jpg" },
    ]},
    { nome: "Pata3D Cortador", plataforma: "Instagram", cor: "#22c55e", posts: [
      { k: "FEED", t: "Cortador gato", hora: "09:45", img: "img/p11.jpg" },
      { k: "REEL", t: "Unboxing", hora: "13:30", img: "img/p4.jpg" },
      { k: "FEED", t: "Kit confeitaria", hora: "15:00", img: "img/p13.jpg" },
      { k: "STORY", t: "Dica rápida", hora: "17:00", img: "img/p18.jpg" },
      { k: "REEL", t: "Resumo da semana", hora: "16:00", img: "img/p16.jpg" },
    ]},
    { nome: "Pata3D Artesanato", plataforma: "Instagram", cor: "#3b82f6", posts: [
      { k: "FEED", t: "Peça pintada", hora: "15:00", img: "img/p5.jpg" },
      { k: "FEED", t: "Decoração boho", hora: "11:00", img: "img/p20.jpg" },
      { k: "REEL", t: "Passo a passo", hora: "18:00", img: "img/p3.jpg" },
      { k: "", t: "", hora: "", img: "" },
      { k: "FEED", t: "Vitrine", hora: "19:30", img: "img/p15.jpg" },
    ]},
    { nome: "Postagem +18", plataforma: "X (Twitter)", cor: "#14b8a6", posts: [
      { k: "POST", t: "Novidade do dia", hora: "08:00", img: "img/p19.jpg" },
      { k: "POST", t: "Promo exclusiva", hora: "12:30", img: "img/p2.jpg" },
      { k: "POST", t: "Enquete", hora: "15:45", img: "img/p8.jpg" },
      { k: "POST", t: "Bastidor", hora: "20:00", img: "img/p12.jpg" },
      { k: "POST", t: "Resumo", hora: "21:30", img: "img/p1.jpg" },
    ]},
  ],
};

// ---- ESTEIRA DE PRODUÇÃO (kanban: etapas do post) ----
DB.esteira = {
  etapas: [
    { id: "ideia", nome: "Ideia", cor: "#3b82f6", cards: [
      { img: "img/p1.jpg", titulo: "3 dicas para o seu cortador", handle: "@pata3d.cortadores", contaId: "cortadores", hora: "10:30", extra: null },
      { img: "img/p12.jpg", titulo: "Bastidores da impressão", handle: "@pata3d.cortadores", contaId: "cortadores", hora: "14:00", extra: null },
    ]},
    { id: "ia", nome: "IA gerou", cor: "#8b5cf6", cards: [
      { img: "img/p2.jpg", titulo: "Vaso decorativo novo", handle: "@pata3d.loja", contaId: "produtos", hora: "11:15", extra: null },
      { img: "img/p9.jpg", titulo: "Coleção completa", handle: "@pata3d.cortadores", contaId: "cortadores", hora: "16:00", extra: null },
      { img: "img/p13.jpg", titulo: "Kit confeitaria", handle: "@pata3d.loja", contaId: "produtos", hora: "18:00", extra: null },
    ]},
    { id: "aprovar", nome: "Aprovar", cor: "#f59e0b", cards: [
      { img: "img/p7.jpg", titulo: "Peça pintada à mão", handle: "@pata3d.artesanato", contaId: "artesanato", hora: "09:45", extra: null },
      { img: "img/p8.jpg", titulo: "Antes e depois", handle: "@pata3d.cortadores", contaId: "cortadores", hora: "12:00", extra: null },
    ]},
    { id: "agendado", nome: "Agendado", cor: "#22c55e", cards: [
      { img: "img/p14.jpg", titulo: "Flor de resina", handle: "@pata3d.loja", contaId: "produtos", hora: "15:00", extra: "cal" },
      { img: "img/p3.jpg", titulo: "Novidade da semana", handle: "@pata3d_x", contaId: "x", hora: "17:30", extra: "cal" },
    ]},
    { id: "publicado", nome: "Publicado", cor: "#14b8a6", cards: [
      { img: "img/p6.jpg", titulo: "Reel coração 3D", handle: "@pata3d.cortadores", contaId: "cortadores", hora: "08:00", extra: "check" },
      { img: "img/p17.jpg", titulo: "Lançamento", handle: "@pata3d.loja", contaId: "produtos", hora: "09:15", extra: "check" },
      { img: "img/p20.jpg", titulo: "Vitrine da loja", handle: "@pata3d.loja", contaId: "produtos", hora: "10:00", extra: "check" },
    ]},
  ],
};

// ---- BIBLIOTECA / CONTEÚDO (galeria + gerenciador de pastas) ----
DB.biblioteca = {
  pastas: [
    { id: "entrada", nome: "Entrada (sem classificar)", cor: "#6a6a7a", itens: [
      { img: "img/p1.jpg", tipo: "foto" }, { img: "img/p2.jpg", tipo: "foto" },
      { img: "img/p3.jpg", tipo: "video" }, { img: "img/p4.jpg", tipo: "foto" },
    ]},
    { id: "pata3d", nome: "Pata3D", cor: "#8b5cf6", itens: [
      { img: "img/p1.jpg", tipo: "foto" }, { img: "img/p2.jpg", tipo: "foto" }, { img: "img/p3.jpg", tipo: "video" },
      { img: "img/p4.jpg", tipo: "foto" }, { img: "img/p5.jpg", tipo: "foto" }, { img: "img/p6.jpg", tipo: "foto" },
    ]},
    { id: "estatua", nome: "Estátua", cor: "#ec4899", itens: [
      { img: "img/p7.jpg", tipo: "foto" }, { img: "img/p8.jpg", tipo: "foto" },
      { img: "img/p9.jpg", tipo: "video" }, { img: "img/p10.jpg", tipo: "foto" },
    ]},
    { id: "cortador", nome: "Cortador", cor: "#22c55e", itens: [
      { img: "img/p11.jpg", tipo: "foto" }, { img: "img/p12.jpg", tipo: "foto" },
      { img: "img/p13.jpg", tipo: "foto" }, { img: "img/p14.jpg", tipo: "video" },
    ]},
    { id: "artesanato", nome: "Artesanato", cor: "#3b82f6", itens: [
      { img: "img/p15.jpg", tipo: "foto" }, { img: "img/p16.jpg", tipo: "foto" }, { img: "img/p17.jpg", tipo: "foto" },
    ]},
    { id: "x18", nome: "X +18", cor: "#14b8a6", itens: [
      { img: "img/p18.jpg", tipo: "foto" }, { img: "img/p19.jpg", tipo: "foto" }, { img: "img/p20.jpg", tipo: "video" },
    ]},
  ],
};

// ---- ESTILOS DE IA por conta (aba Criar) ----
DB.estilosIA = {
  cortadores: ["Produto limpo fundo branco", "Lifestyle cozinha", "Cyberpunk neon"],
  artesanato: ["Rústico aconchegante", "Minimalista claro", "Boho colorido"],
  produtos: ["Catálogo e-commerce", "Flat lay", "Close no detalhe"],
  x: ["Meme/bastidor", "Anúncio direto"],
};

// Helpers simples para pegar conta por id
function contaPorId(id) {
  return DB.contas.find((c) => c.id === id);
}
