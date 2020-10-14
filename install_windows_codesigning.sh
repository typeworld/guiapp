# Decode the environment variable into our file
echo $JANGERNER_CERT > jangerner.cer
echo $CA_CERT > ca.cer
python tweakcertificate.py jangerner.cer
python tweakcertificate.py ca.cer

# Add # https://stackoverflow.com/questions/84847/how-do-i-create-a-self-signed-certificate-for-code-signing-on-windows
certutil -addstore "CA" ca.cer
certutil -addstore -user -f "Jan Gerner" jangerner.cer

exit 1
