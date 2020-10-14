# Set the filename
export CERTIFICATE_CRT=cert.cer;

# Decode the environment variable into our file
echo $CERT_CRT > $CERTIFICATE_CRT
python tweakcertificate.py

cat $CERTIFICATE_CRT

# Add # https://stackoverflow.com/questions/84847/how-do-i-create-a-self-signed-certificate-for-code-signing-on-windows
certutil -user -addstore Root $CERTIFICATE_CRT

exit 1
