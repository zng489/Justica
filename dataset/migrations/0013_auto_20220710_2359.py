# Generated by Django 3.2.9 on 2022-07-10 23:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataset', '0012_auto_20220710_0023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aeronave',
            name='ano_fabricacao',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='Ano de fabricação'),
        ),
        migrations.AlterField(
            model_name='aeronave',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='bemdeclarado',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='bemdeclarado',
            name='tipo',
            field=models.SmallIntegerField(choices=[(1, 'Prédio residencial'), (2, 'Prédio comercial'), (3, 'Galpão'), (11, 'Apartamento'), (12, 'Casa'), (13, 'Terreno'), (14, 'Terra Nua'), (15, 'Sala ou Conjunto'), (16, 'Construção'), (17, 'Benfeitorias'), (18, 'Loja'), (19, 'Outros bens imóveis'), (21, 'Veículo automotor terrestre (caminhão, automóvel, moto etc.)'), (22, 'Aeronave'), (23, 'Embarcação'), (24, 'Bem relacionado com o exercício da atividade autônoma'), (25, 'Jóia, Quadro, Objeto de arte, de coleção, Antiguidade etc.'), (26, 'Linha telefônica'), (29, 'Outros bens móveis'), (31, 'Ações (inclusive provenientes de linha telef.)'), (32, 'Quotas ou Quinhões de capital'), (39, 'Outras participações societárias'), (41, 'Caderneta de poupança'), (45, 'Aplicação de renda fixa (CDB, RDB e outros)'), (46, 'Ouro, Ativo financeiro'), (47, 'Mercado futuros, de opções e a termo'), (49, 'Outras aplicações e investimentos'), (51, 'Crédito decorrente de empréstimo'), (52, 'Crédito decorrente de alienação'), (53, 'Plano PAIT e Caderneta de pecúlio'), (54, 'Poupança para construção ou aquisição de bem imóvel'), (59, 'Outros créditos e Poupança vinculados'), (61, 'Depósito bancário em conta corrente no país'), (62, 'Depósito bancário em conta corrente no exterior'), (63, 'Dinheiro em espécie - Moeda nacional'), (64, 'Dinheiro em espécie - Moeda estrangeira'), (69, 'Outros depósitos à vista e numerário'), (71, 'Fundo de investimento financeiro - FIF'), (71, 'Fundo de curto prazo'), (72, 'Fundo de aplicação em quotas de fundos de investimento'), (72, 'Fundo de longo prazo e Fundo de investimentos em direitos creditórios (FIDC)'), (73, 'Fundo de capitalização'), (73, 'Fundo de investimento imobiliário'), (74, 'Fundos: ações, mútuos de privatização, invest. empresas emergentes, invest. participação e invest. índice mercado'), (74, 'Fundo de ações, inclusive carteira livre e Fundo de investimento no exterior'), (79, 'Outros fundos'), (91, 'Licença e Concessões especiais'), (92, 'Título de clube e assemelhado'), (93, 'Direito de autor, de inventor e patente'), (94, 'Direito de lavra e assemelhado'), (95, 'Consórcio não contemplado'), (96, 'Leasing'), (97, 'VGBL - Vida Gerador de Benefício Livre'), (99, 'Outros bens e direitos')], help_text='Tipo do bem declarado', verbose_name='Tipo'),
        ),
        migrations.AlterField(
            model_name='candidacy',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='company',
            name='codigo_motivo_situacao_cadastral',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='codigo_municipio',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='codigo_natureza_juridica',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='codigo_pais',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='codigo_porte',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='codigo_qualificacao_responsavel',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='codigo_situacao_cadastral',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='embarcacao',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='person',
            name='ano_exercicio_ocupacao',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='ano_obito',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='codigo_natureza_ocupacao',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='codigo_ocupacao_principal',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='sancao',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]