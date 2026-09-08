-- Firebase/FCM is no longer part of MadWorld.
-- Remove the obsolete device-token registry and any stored provider tokens.
DROP TABLE IF EXISTS device_push_tokens;
