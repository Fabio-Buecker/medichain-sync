-- Guarda somente a visao consolidada mais recente de cada paciente.
-- Cria a tabela indicada caso ela ainda não exista.
CREATE TABLE IF NOT EXISTS record_state (
    -- Identificador do paciente ao qual o registro pertence; chave primária única.
    patient_id TEXT PRIMARY KEY,
    -- Campos atuais do prontuário serializados em JSON; preenchimento obrigatório.
    data_json TEXT NOT NULL,
    -- Vetor das clínicas usado para comparar as atualizações; preenchimento obrigatório.
    clinical_clock_json TEXT NOT NULL,
    -- Identificador do último evento escolhido para o estado; preenchimento obrigatório.
    last_event_id TEXT NOT NULL
-- Encerra a declaração da tabela.
);

-- Preserva todas as decisoes para rastreabilidade e ordenacao causal.
-- Cria a tabela indicada caso ela ainda não exista.
CREATE TABLE IF NOT EXISTS audit_log (
    -- Identificador único usado para impedir gravação duplicada; chave primária única.
    event_id TEXT PRIMARY KEY,
    -- Identificador do paciente ao qual o registro pertence; preenchimento obrigatório.
    patient_id TEXT NOT NULL,
    -- Número do worker que processou o evento; preenchimento obrigatório.
    worker_id INTEGER NOT NULL,
    -- Número do líder que consolidou o evento; preenchimento obrigatório.
    leader_id INTEGER NOT NULL,
    -- Relação encontrada na comparação dos vetores; preenchimento obrigatório.
    causal_relation TEXT NOT NULL,
    -- Decisão tomada na consolidação; preenchimento obrigatório.
    decision TEXT NOT NULL,
    -- Vetor das clínicas usado para comparar as atualizações; preenchimento obrigatório.
    clinical_clock_json TEXT NOT NULL,
    -- Vetor de processamento registrado pelo worker; preenchimento obrigatório.
    processing_clock_json TEXT NOT NULL
-- Encerra a declaração da tabela.
);

-- Registra atualizacoes concorrentes que precisam permanecer auditaveis.
-- Cria a tabela indicada caso ela ainda não exista.
CREATE TABLE IF NOT EXISTS conflicts (
    -- Identificador único usado para impedir gravação duplicada; chave primária única.
    event_id TEXT PRIMARY KEY,
    -- Identificador do paciente ao qual o registro pertence; preenchimento obrigatório.
    patient_id TEXT NOT NULL,
    -- Evento que já representava o estado antes do conflito; preenchimento obrigatório.
    existing_event_id TEXT NOT NULL,
    -- Valor recebido no evento em conflito; preenchimento obrigatório.
    incoming_value TEXT NOT NULL,
    -- Decisão tomada na consolidação; preenchimento obrigatório.
    decision TEXT NOT NULL
-- Encerra a declaração da tabela.
);
