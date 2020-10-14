# Set the filename
export CERTIFICATE=cert.cer;

# Decode the environment variable into our file
echo $CERT_CER > $CERTIFICATE
python tweakcertificate.py

# Add # https://stackoverflow.com/questions/84847/how-do-i-create-a-self-signed-certificate-for-code-signing-on-windows
certutil -addstore "Root" $CERTIFICATE
#certutil -addstore -user -f "Jan Gerner" $CERTIFICATE

exit 1
