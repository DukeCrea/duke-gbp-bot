# 🚀 Guía de Deployment en Railway

## Paso 1: Preparar GitHub

Si aún no lo hiciste:

```bash
git init
git add .
git commit -m "Initial commit: DukeGBP Bot"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/duke_gbp_bot.git
git push -u origin main
```

## Paso 2: Conectar Railway

1. Ve a https://railway.app
2. Sign in con GitHub
3. Click en **"New Project"**
4. Selecciona **"Deploy from GitHub"**
5. Autoriza GitHub y selecciona tu repo `duke_gbp_bot`

## Paso 3: Agregar Variables de Entorno

En Railway, ve a **Variables**:

```
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET
CLAUDE_API_KEY=YOUR_CLAUDE_API_KEY
ENVIRONMENT=production
```

## Paso 4: Deploy

1. Railway detecta automáticamente el **Dockerfile**
2. Construye la imagen Docker
3. Despliega el contenedor
4. El bot comienza a funcionar

## Paso 5: Verificar

Ve a **Logs** en Railway y deberías ver:

```
🚀 DukeGBP Bot iniciado...
```

## ¡Listo! 🎉

Tu bot estará vivo en Railway. Abre Telegram y escribe `/start` a `@DukegbpBot`.

---

## Troubleshooting

### El bot no responde
- Revisa los **Logs** en Railway
- Verifica que todas las **Variables** están configuradas
- Asegúrate que el **Token de Telegram** es correcto

### Error "credentials.json not found"
- El archivo está en la raíz del proyecto
- Railway lo debería copiar automáticamente
- Si falla, agregalo en el Dockerfile

### Error de autenticación con Google
- Verifica Client ID y Secret en `.env`
- Las APIs deben estar habilitadas en Google Cloud Console

---

## Próximos pasos

1. **Webhook en lugar de polling** (más eficiente)
2. **Dashboard web** para ver análisis
3. **Alertas automáticas** cuando GMB cambia

¿Necesitas ayuda con algo?
