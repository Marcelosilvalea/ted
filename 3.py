from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class Produto:
    nome: str
    preco: float


@dataclass
class Cliente:
    nome: str
    endereco: str
    pedidos: List["Pedido"] = field(default_factory=list)


@dataclass
class Restaurante:
    nome: str
    tempo_preparo_min: int
    aceita_automaticamente: bool = True

    def avaliar_pedido(self, pedido: "Pedido") -> bool:
        return self.aceita_automaticamente


@dataclass
class Entregador:
    nome: str
    disponivel: bool = True


@dataclass
class Pedido:
    cliente: Cliente
    restaurante: Restaurante
    itens: List[Produto]
    status: str = "criado"
    tempo_estimado_min: Optional[int] = None
    entregador: Optional[Entregador] = None

    def total(self) -> float:
        return sum(item.preco for item in self.itens)


class Pagamento:
    @staticmethod
    def processar(pedido: Pedido, simular_falha: bool = False) -> bool:
        if simular_falha:
            return False
        return True


class SistemaDelivery:
    def __init__(self):
        self.pedidos: List[Pedido] = []

    def realizar_pedido(self, cliente: Cliente, restaurante: Restaurante,
                         itens: List[Produto], entregadores: List[Entregador],
                         simular_falha_pagamento: bool = False) -> Optional[Pedido]:
        print(f"\n[1] {cliente.nome} seleciona produtos: "
              f"{[p.nome for p in itens]}.")

        pedido = Pedido(cliente=cliente, restaurante=restaurante, itens=itens)

        print(f"[2] Pedido confirmado. Total: R$ {pedido.total():.2f}.")

        pagamento_aprovado = Pagamento.processar(pedido, simular_falha=simular_falha_pagamento)
        if not pagamento_aprovado:
            pedido.status = "pagamento_falho"
            print("[2A] Falha no pagamento. Pedido não será enviado ao restaurante.")
            self.pedidos.append(pedido)
            return None

        pedido.status = "pago"
        print("[2] Pagamento aprovado.")
        print(f"[3] Pedido enviado ao restaurante '{restaurante.nome}'.")

        if not restaurante.avaliar_pedido(pedido):
            pedido.status = "recusado"
            print("[4A] Restaurante recusou o pedido.")
            self.pedidos.append(pedido)
            return None

        pedido.status = "preparando"
        print("[4] Restaurante aceitou o pedido.")

        pedido.tempo_estimado_min = restaurante.tempo_preparo_min + 15
        print(f"[Regra] Tempo estimado informado ao cliente: "
              f"{pedido.tempo_estimado_min} minutos.")

        print(f"[5] Pedido em preparo (aprox. {restaurante.tempo_preparo_min} min).")

        disponiveis = [e for e in entregadores if e.disponivel]
        if not disponiveis:
            print("[!] Nenhum entregador disponível no momento.")
            self.pedidos.append(pedido)
            return pedido

        entregador = disponiveis[0]
        entregador.disponivel = False
        pedido.entregador = entregador
        pedido.status = "em_entrega"
        print(f"[6] Entregador '{entregador.nome}' saiu para entrega.")

        pedido.status = "entregue"
        entregador.disponivel = True
        print(f"[7] {cliente.nome} recebeu o pedido.")

        self.pedidos.append(pedido)
        cliente.pedidos.append(pedido)
        return pedido


def escolher_da_lista(itens: Dict[str, object], rotulo: str):
    if not itens:
        print(f"Nenhum(a) {rotulo} cadastrado(a) ainda.")
        return None
    chaves = list(itens.keys())
    for i, chave in enumerate(chaves, start=1):
        print(f"  {i}. {chave}")
    escolha = input(f"Escolha o número do(a) {rotulo}: ").strip()
    if not escolha.isdigit() or not (1 <= int(escolha) <= len(chaves)):
        print("Escolha inválida.")
        return None
    return itens[chaves[int(escolha) - 1]]


def cadastrar_cliente(clientes: Dict[str, Cliente]):
    nome = input("Nome do cliente: ").strip()
    endereco = input("Endereço: ").strip()
    clientes[nome] = Cliente(nome=nome, endereco=endereco)
    print(f"Cliente '{nome}' cadastrado.")


def cadastrar_restaurante(restaurantes: Dict[str, Restaurante]):
    nome = input("Nome do restaurante: ").strip()
    try:
        tempo = int(input("Tempo de preparo (min): "))
    except ValueError:
        tempo = 30
    aceita = input("O restaurante aceita pedidos automaticamente? (s/n): ").strip().lower() != "n"
    restaurantes[nome] = Restaurante(nome=nome, tempo_preparo_min=tempo,
                                      aceita_automaticamente=aceita)
    print(f"Restaurante '{nome}' cadastrado.")


def cadastrar_entregador(entregadores: Dict[str, Entregador]):
    nome = input("Nome do entregador: ").strip()
    entregadores[nome] = Entregador(nome=nome)
    print(f"Entregador '{nome}' cadastrado.")


def montar_itens_pedido() -> List[Produto]:
    itens = []
    try:
        qtd = int(input("Quantos itens deseja adicionar ao pedido? "))
    except ValueError:
        return itens
    for i in range(qtd):
        nome = input(f"Nome do item {i + 1}: ").strip()
        try:
            preco = float(input(f"Preço do item {i + 1}: R$ "))
        except ValueError:
            preco = 0.0
        itens.append(Produto(nome=nome, preco=preco))
    return itens


def realizar_pedido_interativo(sistema: SistemaDelivery,
                                clientes: Dict[str, Cliente],
                                restaurantes: Dict[str, Restaurante],
                                entregadores: Dict[str, Entregador]):
    print("\nSelecione o cliente:")
    cliente = escolher_da_lista(clientes, "cliente")
    if cliente is None:
        return

    print("\nSelecione o restaurante:")
    restaurante = escolher_da_lista(restaurantes, "restaurante")
    if restaurante is None:
        return

    itens = montar_itens_pedido()
    if not itens:
        print("Nenhum item informado.")
        return

    simular_falha = input("Simular falha no pagamento? (s/n): ").strip().lower() == "s"

    sistema.realizar_pedido(cliente, restaurante, itens,
                             list(entregadores.values()),
                             simular_falha_pagamento=simular_falha)


def listar_pedidos(sistema: SistemaDelivery):
    if not sistema.pedidos:
        print("Nenhum pedido registrado.")
        return
    for p in sistema.pedidos:
        print(f"- {p.cliente.nome} em '{p.restaurante.nome}' "
              f"total R$ {p.total():.2f} [{p.status}]")


def menu():
    sistema = SistemaDelivery()
    clientes: Dict[str, Cliente] = {}
    restaurantes: Dict[str, Restaurante] = {}
    entregadores: Dict[str, Entregador] = {}

    opcoes = {
        "1": ("Cadastrar cliente", lambda: cadastrar_cliente(clientes)),
        "2": ("Cadastrar restaurante", lambda: cadastrar_restaurante(restaurantes)),
        "3": ("Cadastrar entregador", lambda: cadastrar_entregador(entregadores)),
        "4": ("Realizar pedido", lambda: realizar_pedido_interativo(sistema, clientes, restaurantes, entregadores)),
        "5": ("Listar pedidos", lambda: listar_pedidos(sistema)),
        "0": ("Sair", None),
    }

    while True:
        print("\n=== Sistema de Delivery de Comida ===")
        for chave, (texto, _) in opcoes.items():
            print(f"{chave}. {texto}")
        escolha = input("Escolha uma opção: ").strip()

        if escolha == "0":
            print("Encerrando.")
            break
        if escolha in opcoes:
            opcoes[escolha][1]()
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()
