from opensearch_dsl import Document, Integer, Ip, Keyword, Search, Text
from opensearchpy import OpenSearch, TransportError

index_name = "sniper_audit_logs"


class SniperAuditLogs(Document):
    auditID = Keyword()
    remoteAddr = Ip()
    remotePort = Integer()
    cnpjPesquisado = Keyword()
    argumentosPesquisa = Text()
    cpfUsuarioConsulta = Keyword()
    # pesquisaTimestamp = Date()

    class Index:
        name = index_name

    def save(self, **kwargs):
        return super(SniperAuditLogs, self).save(**kwargs)


host = "opensearch.stg.pdpj.jus.br"
port = 443
f = open("passw.txt", "r")
passw = f.read()
print(passw)
auth = ("rosfran.borges", passw)
# ca_certs_path = '/full/path/to/root-ca.pem' # Provide a CA bundle if you use intermediate CAs with your root CA.

# Create the client with SSL/TLS enabled, but hostname verification disabled.
client = OpenSearch(
    hosts=[{"host": host, "port": port}],
    http_compress=False,  # enables gzip compression for request bodies
    http_auth=auth,
    use_ssl=True,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)

# index_body = {
#   'settings': {
#     'index': {
#       'number_of_shards': 4
#     }
#   }
# }

# response = client.indices.create(index_name, body=index_body)

# SniperAuditLogs.init(using=client)
doc = SniperAuditLogs(
    auditID="18281",
    remoteAddr="212.176.12.189",
    remotePort=8191,
    cnpjPesquisado="59032731000161",
    argumentosPesquisa="empresa gepeto ltda.",
    cpfUsuarioConsulta="56771002420",
)


# Insert data into the index
actions = []
indexValue = doc.to_dict(include_meta=True)
indexValue["@timestamp"] = "2024-03-21T12:00:00"
actions.append(actions.append({"_op_type": "create", "_index": index_name, "_source": indexValue}))

print("--> ", doc.to_dict(include_meta=True))


# actions.append(actions.append({"_op_type": "create", "_index": index_name, \
#                                "_source": \
#                                   {  \
#                                       "auditID": "18281", \
#                                       "remoteAddr": "212.176.12.189", \
#                                       "remotePort": "8191",
#                                       "cnpjPesquisado": "59.032.731/0001-61",
#                                       "argumentosPesquisa": "empresa gepeto ltda.", \
#                                       "cpfUsuarioConsulta": "56771002420"
#                                   }
#                                }))

# bulk(client,actions)
# actions.append(actions.append({ "create": { "_source": doc.to_dict(include_meta=True) }}))
# client.bulk(actions)


# response = doc.save(using=client, op_type="create")

print("------> ", doc)
try:
    response = doc.save(using=client, validate=False)
except TransportError as e:
    print(e.info)


data = {
    "@timestamp": "2024-03-21T12:00:00",
    "argumentosPesquisa": "example arguments",
    "auditID": "example_audit_id",
    "cnpjPesquisado": "example_cnpj",
    "cpfUsuarioConsulta": "example_cpf",
    "detalhesParametrosPesquisa": {"param1": "value1", "param2": "value2"},
    "nomeUsuarioConsulta": "example_username",
    "pesquisaTimestamp": "2024-03-21T12:00:00",
    "quantidadeResultados": 10,
    "remoteAddr": "192.168.1.1",
    "remotePort": 12345,
    "resultadoPesquisa": {"result1": "value1", "result2": "value2"},
    "usuarioExtraData": {"extra1": "value1", "extra2": "value2"},
    "usuarioGeoIP": {"lat": 40.12, "lon": -71.34},
}

# Index your data into OpenSearch
response = client.index(index=index_name, body=data)

print("Data stored successfully.")

s = Search(using=client, index=index_name).query("match", title="*")

response = s.execute()
