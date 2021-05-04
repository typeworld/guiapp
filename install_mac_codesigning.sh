# Install macOS Code Signing Certificate
# see https://felixrieseberg.com/codesigning-electron-apps-in-ci/
# great discussion on https://stackoverflow.com/questions/39868578/security-codesign-in-sierra-keychain-ignores-access-control-settings-and-ui-p

# Set the filename
# export CERTIFICATE_P12=cert.p12;

# Decode the environment variable into our file
# echo $MACOS_CERT_P12 | base64 --decode > $CERTIFICATE_P12;

# Let's invent a new keychain
export KEYCHAIN=build.keychain;

# Create the keychain with a password (travis)
security create-keychain -p travis $KEYCHAIN;

# Make the custom keychain default, so xcodebuild will use it for signing
security default-keychain -s $KEYCHAIN;

# On top of that the keychain must be added to the search list:
security list-keychains -s $KEYCHAIN

# Unlock the keychain
security unlock-keychain -p travis $KEYCHAIN;

# Add certificates to keychain and allow codesign to access them

# Possibly download latest certificates from here_ https://www.apple.com/certificateauthority/
# 1) Apple Worldwide Developer Relations Certification Authority
security import wxPython/build/Mac/codesigning/AppleWWDRCA.cer -k ~/Library/Keychains/$KEYCHAIN -T /usr/bin/codesign
# 2) Developer Authentication Certification Authority
security import wxPython/build/Mac/codesigning/DevAuthCA.cer -k ~/Library/Keychains/$KEYCHAIN -T /usr/bin/codesign
# 3) Developer ID (That's you!)
security import wxPython/build/Mac/codesigning/jangerner.p12 -k ~/Library/Keychains/$KEYCHAIN -P $MACOS_CERT_PASSWORD -T /usr/bin/codesign
# 2>&1 >/dev/null;

# Then the keychain should be unlocked. Otherwise a prompt asking for the keychain password will be displayed:
security unlock-keychain -p travis $KEYCHAIN

# Eventually the auto-lock timeout should be disabled. This is in case the build is quite long and the keychain re-locks itself:
security set-keychain-settings $KEYCHAIN

# Let's delete the file, we no longer need it
# rm $CERTIFICATE_P12;

# Set the partition list (sort of like an access control list)
security set-key-partition-list -S apple-tool:,apple: -s -k travis $KEYCHAIN

# Echo the identity, just so that we know it worked.
# This won't display anything secret.
security find-identity -v -p codesigning

