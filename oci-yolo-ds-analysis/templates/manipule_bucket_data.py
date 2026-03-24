
import io
import oci


config_oci = oci.config.from_file("path to .oci/config") # Substitua pelo caminho para o arquivo de configuração OCI
object_storage = oci.object_storage.ObjectStorageClient(config_oci)

# the response.data.objects contains the list of objects in the specified bucket and prefix
response = object_storage.list_objects(
    namespace_name='bucket_namespace',  # Substitua pelo namespace do seu bucket
    bucket_name="bucket_name", # Substitua pelo nome do seu bucket
    prefix="prefix" # Substitua pelo prefixo da pasta onde estão os arquivos
)

# the response.data.content contains the bytes of the downloaded object
response = object_storage.get_object(
    namespace_name='bucket_namespace',  # Substitua pelo namespace do seu bucket
    bucket_name="bucket_name", # Substitua pelo nome do seu bucket
    object_name="path" # Substitua pela rota do arquivo que deseja obter
)


# to load the bytes into a variable, you can use io.BytesIO
loaded_data = io.BytesIO(response.data.content)