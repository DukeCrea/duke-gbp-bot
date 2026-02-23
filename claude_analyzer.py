import json
import logging
from typing import Dict, Any
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class ClaudeAnalyzer:
    """Analiza datos de GMB usando Claude AI"""
    
    def __init__(self, api_key: str):
        """
        Inicializar analizador
        
        Args:
            api_key: Clave de API de Anthropic
        """
        self.client = Anthropic()
        self.client.api_key = api_key
    
    async def analyze_gmb(self, gmb_data: Dict[str, Any]) -> str:
        """
        Analizar datos de GMB y generar recomendaciones
        
        Args:
            gmb_data: Datos del negocio obtenidos de las APIs
            
        Returns:
            Análisis formateado como string
        """
        try:
            # Extraer información relevante
            profile = gmb_data.get('profile', {})
            performance = gmb_data.get('performance', {})
            
            # Compilar prompt con datos
            analysis_prompt = self._build_prompt(profile, performance)
            
            # Llamar a Claude
            response = self.client.messages.create(
                model="claude-opus-4-5-20251101",
                max_tokens=1500,
                messages=[
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Error analizando con Claude: {e}")
            return f"❌ Error al generar análisis: {str(e)}"
    
    def _build_prompt(self, profile: Dict, performance: Dict) -> str:
        """
        Construir prompt para Claude
        
        Args:
            profile: Datos del perfil
            performance: Métricas de performance
            
        Returns:
            Prompt formateado
        """
        
        # Compilar información del perfil
        profile_info = f"""
## Información del Perfil:
- Nombre: {profile.get('title', 'N/A')}
- Categoría: {profile.get('type', 'N/A')}
- Teléfono: {profile.get('phoneNumber', 'N/A')}
- Sitio web: {profile.get('websiteUrl', 'N/A')}
- Descripción: {profile.get('description', 'N/A')[:200]}...
- Dirección: {profile.get('address', {}).get('addressLines', ['N/A'])[0] if profile.get('address') else 'N/A'}
- Horarios: {profile.get('businessHours', 'N/A')}
- Fotos: {len(profile.get('photos', []))} fotos subidas
"""
        
        # Compilar métricas
        performance_info = f"""
## Métricas (últimos 30 días):
- Vistas: {performance.get('views', 0):,}
- Búsquedas directas: {performance.get('queries_direct', 0):,}
- Búsquedas indirectas: {performance.get('queries_indirect', 0):,}
- Llamadas: {performance.get('calls', 0):,}
- Direcciones solicitadas: {performance.get('directions', 0):,}
- Clics al sitio: {performance.get('website_clicks', 0):,}
"""
        
        prompt = f"""Eres un experto en optimización de Google My Business (GMB). 
Analiza el siguiente perfil de negocio y proporciona un reporte detallado en español con:

1. **Puntuación General** (0-100): Califica la optimización del perfil
2. **Análisis Fortalezas**: Qué está bien hecho
3. **Áreas de Mejora**: Qué se puede optimizar
4. **Recomendaciones Prioritarias**: Top 3 acciones para mejorar visibilidad
5. **Estimación de Impacto**: Qué resultados se podrían esperar

{profile_info}

{performance_info}

Sé específico, conciso y actionable. Usa emojis para hacerlo legible. 
Proporciona recomendaciones que el usuario pueda implementar hoy mismo."""
        
        return prompt
    
    def _parse_analysis(self, response_text: str) -> Dict[str, Any]:
        """
        Parsear respuesta de Claude (opcional para análisis estructurado)
        
        Args:
            response_text: Texto de respuesta de Claude
            
        Returns:
            Dict con análisis estructurado
        """
        # Por ahora, retornar como string
        # En futuro, podrías parsearlo en secciones
        return {
            'analysis': response_text
        }
