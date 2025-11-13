-- Criar o banco de dados
CREATE DATABASE sistema_vendas;
\c sistema_vendas;

-- Tabela de Clientes
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    telefone VARCHAR(20),
    data_cadastro DATE DEFAULT CURRENT_DATE,
    cidade VARCHAR(50),
    estado VARCHAR(2)
);

-- Tabela de Categorias
CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    descricao TEXT
);

-- Tabela de Produtos
CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    preco_custo DECIMAL(10,2),
    preco_venda DECIMAL(10,2),
    estoque INTEGER DEFAULT 0,
    categoria_id INTEGER REFERENCES categorias(id),
    data_cadastro DATE DEFAULT CURRENT_DATE
);

-- Tabela de Vendas
CREATE TABLE vendas (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id),
    data_venda DATE DEFAULT CURRENT_DATE,
    valor_total DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'finalizada'
);

-- Tabela de Itens da Venda
CREATE TABLE itens_venda (
    id SERIAL PRIMARY KEY,
    venda_id INTEGER REFERENCES vendas(id),
    produto_id INTEGER REFERENCES produtos(id),
    quantidade INTEGER NOT NULL,
    preco_unitario DECIMAL(10,2),
    subtotal DECIMAL(10,2)
);

-- Inserir categorias
INSERT INTO categorias (nome, descricao) VALUES
('Eletrônicos', 'Produtos eletrônicos em geral'),
('Informática', 'Computadores e periféricos'),
('Móveis', 'Móveis para escritório');

-- Inserir produtos
INSERT INTO produtos (nome, descricao, preco_custo, preco_venda, estoque, categoria_id) VALUES
('Notebook Dell', 'Notebook Dell i5 8GB', 2000.00, 2800.00, 15, 2),
('Mouse Wireless', 'Mouse sem fio', 30.00, 79.90, 50, 2),
('Teclado Mecânico', 'Teclado mecânico RGB', 120.00, 299.00, 25, 2),
('Smartphone Samsung', 'Samsung Galaxy S20', 1800.00, 2400.00, 30, 1),
('Cadeira Gamer', 'Cadeira gamer ergonômica', 450.00, 899.00, 10, 3);

-- Inserir clientes
INSERT INTO clientes (nome, email, telefone, cidade, estado) VALUES
('João Silva', 'joao@email.com', '(11)9999-8888', 'São Paulo', 'SP'),
('Maria Santos', 'maria@email.com', '(21)8888-7777', 'Rio de Janeiro', 'RJ'),
('Pedro Oliveira', 'pedro@email.com', '(31)7777-6666', 'Belo Horizonte', 'MG');

-- Inserir vendas
INSERT INTO vendas (cliente_id, data_venda, valor_total) VALUES
(1, '2024-01-15', 3098.90),
(2, '2024-01-16', 5998.00),
(1, '2024-01-17', 1797.00),
(3, '2024-01-18', 899.00);

-- Inserir itens das vendas
INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario, subtotal) VALUES
(1, 1, 1, 2800.00, 2800.00),
(1, 2, 2, 79.90, 159.80),
(1, 3, 1, 299.00, 299.00),
(2, 1, 2, 2800.00, 5600.00),
(2, 4, 1, 2400.00, 2400.00),
(3, 2, 5, 79.90, 399.50),
(3, 3, 3, 299.00, 897.00),
(4, 5, 1, 899.00, 899.00);
