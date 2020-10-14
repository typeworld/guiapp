# Decode the environment variable into our file
echo $CERTUM_TRUSTED_NETWORK_CA > CERTUM_TRUSTED_NETWORK_CA.cer
echo $SSL_COM_ROOT_CERTIFICATION_AUTHORITY_RSA > SSL_COM_ROOT_CERTIFICATION_AUTHORITY_RSA.cer
echo $SSL_COM_CODE_SIGNING_INTERMEDIATE_CA_RSA_R1 > SSL_COM_CODE_SIGNING_INTERMEDIATE_CA_RSA_R1.cer
echo $JANGERNER_CERT > JANGERNER_CERT.cer

python tweakcertificate.py CERTUM_TRUSTED_NETWORK_CA.cer
python tweakcertificate.py SSL_COM_ROOT_CERTIFICATION_AUTHORITY_RSA.cer
python tweakcertificate.py SSL_COM_CODE_SIGNING_INTERMEDIATE_CA_RSA_R1.cer
python tweakcertificate.py JANGERNER_CERT.cer

# Add
# https://stackoverflow.com/questions/23869177/import-certificate-to-trusted-root-but-not-to-personal-command-line
certutil -addstore "Root" CERTUM_TRUSTED_NETWORK_CA.cer
certutil -addstore "CA" SSL_COM_ROOT_CERTIFICATION_AUTHORITY_RSA.cer
certutil -addstore "CA" SSL_COM_CODE_SIGNING_INTERMEDIATE_CA_RSA_R1.cer
certutil -addstore -user -f "My" JANGERNER_CERT.cer

