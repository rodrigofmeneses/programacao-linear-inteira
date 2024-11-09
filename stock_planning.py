import pyomo.environ as pyo


def build_model():
    model = pyo.ConcreteModel()

    # Sets
    model.PRODUTOS = pyo.Set(initialize=["A", "B"])
    model.MESES = pyo.Set(initialize=[1, 2])

    # Parameters
    model.Demanda = pyo.Param(
        model.PRODUTOS,
        initialize={
            "A": 500,
            "B": 700,
        },
    )

    model.CustoProducao = pyo.Param(
        model.PRODUTOS,
        model.MESES,
        initialize={
            ("A", 1): 52,
            ("A", 2): 23,
            ("B", 1): 100,
            ("B", 2): 60,
        },
    )

    model.CustoEstoqueProduto = pyo.Param(
        model.PRODUTOS, initialize={"A": 0.10, "B": 0.20}
    )

    model.CustoEstoqueMateriaPrima = pyo.Param(initialize=0.01)

    model.CustoMaoDeObra = pyo.Param(model.PRODUTOS, initialize={"A": 0.5, "B": 0.8})
    model.CustoMateriaPrima = pyo.Param(
        model.PRODUTOS,
        initialize={
            "A": 10,
            "B": 7,
        },
    )

    model.DisponibilidadeMaoDeObra = pyo.Param(model.MESES, initialize={1: 350, 2: 500})
    model.DisponibilidadeMateriaPrima = pyo.Param(
        model.MESES, initialize={1: 6000, 2: 4000}
    )

    # Variables
    model.producao = pyo.Var(
        model.PRODUTOS, model.MESES, domain=pyo.NonNegativeIntegers
    )
    model.estoques_produto = pyo.Var(model.PRODUTOS, domain=pyo.NonNegativeIntegers)
    model.estoque_materia_prima = pyo.Var(domain=pyo.NonNegativeIntegers)

    # Constraints
    @model.Constraint(model.PRODUTOS)
    def atendimento_demandas(model, produto):
        return (
            sum(model.producao[produto, mes] for mes in model.MESES)
            == model.Demanda[produto]
        )

    @model.Constraint(model.MESES)
    def capacidade_mao_de_obra(model, mes):
        return (
            sum(
                model.CustoMaoDeObra[produto] * model.producao[produto, mes]
                for produto in model.PRODUTOS
            )
            <= model.DisponibilidadeMaoDeObra[mes]
        )

    @model.Constraint()
    def capacidade_materia_prima_mes_1(model):
        return (
            sum(
                model.CustoMateriaPrima[produto] * model.producao[produto, 1]
                for produto in model.PRODUTOS
            )
            <= model.DisponibilidadeMateriaPrima[1]
        )

    @model.Constraint()
    def capacidade_materia_prima_mes_2(model):
        return (
            sum(
                model.CustoMateriaPrima[produto] * model.producao[produto, 2]
                for produto in model.PRODUTOS
            )
            <= model.estoque_materia_prima + model.DisponibilidadeMateriaPrima[2]
        )

    @model.Constraint()
    def definir_estoque_materia_prima(model):
        return model.estoque_materia_prima == model.DisponibilidadeMateriaPrima[
            1
        ] - sum(
            model.CustoMateriaPrima[produto] * model.producao[produto, 1]
            for produto in model.PRODUTOS
        )

    # Objective Function
    def objective_function(model):
        return (
            sum(
                model.CustoProducao[produto, mes] * model.producao[produto, mes]
                for produto in model.PRODUTOS
                for mes in model.MESES
            )
            + sum(
                model.CustoEstoqueProduto[produto] * model.estoques_produto[produto]
                for produto in model.PRODUTOS
            )
            + model.CustoEstoqueMateriaPrima * model.estoque_materia_prima
        )

    model.objective = pyo.Objective(rule=objective_function, sense=pyo.minimize)

    return model


if __name__ == "__main__":
    model = build_model()
    solver = pyo.SolverFactory("cbc")
    solver.solve(model)

    for produto in model.PRODUTOS:
        for mes in model.MESES:
            print(
                f"Produção de {produto} no mês {mes}: {model.producao[produto, mes].value}"
            )

    for produto in model.PRODUTOS:
        print(f"Estoque de {produto}: {model.estoques_produto[produto].value}")

    print(f"Estoque de matéria-prima: {model.estoque_materia_prima.value}")
    print(f"Custo total: {model.objective()}")
