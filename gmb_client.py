import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

logger = logging.getLogger(__name__)


class GMBClient:
    """Cliente para Google My Business APIs"""
    
    def __init__(self, credentials: Credentials):
        """
        Inicializar cliente GMB
        
        Args:
            credentials: Google OAuth credentials
        """
        self.credentials = credentials
        self.business_service = build('mybusiness', 'v4', credentials=credentials)
        self.business_profile_service = build('mybusinessbusinessinformation', 'v1', credentials=credentials)
        self.performance_service = build('mybusinessperformance', 'v1', credentials=credentials)
    
    async def get_business_data(self) -> Optional[Dict[str, Any]]:
        """
        Obtener datos completos del negocio
        
        Returns:
            Dict con información del negocio
        """
        try:
            # 1. Obtener lista de negocios
            accounts = self.business_service.accounts().list().execute()
            
            if not accounts.get('accounts'):
                logger.warning("No se encontraron cuentas de negocio")
                return None
            
            # Usar la primera cuenta
            account = accounts['accounts'][0]
            account_name = account['name']
            
            # 2. Obtener ubicaciones (locations)
            locations = self.business_service.accounts().locations().list(
                parent=account_name
            ).execute()
            
            if not locations.get('locations'):
                logger.warning("No se encontraron ubicaciones")
                return None
            
            # Usar la primera ubicación
            location = locations['locations'][0]
            location_name = location['name']
            
            # 3. Obtener información del perfil
            profile = self.business_profile_service.locations().get(
                name=location_name
            ).execute()
            
            # 4. Obtener métricas de performance
            performance_data = await self.get_performance_metrics(location_name)
            
            # 5. Compilar datos
            business_data = {
                'account_name': account_name,
                'location_name': location_name,
                'profile': profile,
                'performance': performance_data
            }
            
            return business_data
            
        except Exception as e:
            logger.error(f"Error obteniendo datos de GMB: {e}")
            return None
    
    async def get_performance_metrics(self, location_name: str) -> Dict[str, Any]:
        """
        Obtener métricas de performance del último mes
        
        Args:
            location_name: Nombre de la ubicación
            
        Returns:
            Dict con métricas
        """
        try:
            # Últimos 30 días
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            
            metrics_request = self.performance_service.locations().reportInsights(
                location=location_name,
                body={
                    'dateRange': {
                        'startDate': {
                            'year': start_date.year,
                            'month': start_date.month,
                            'day': start_date.day
                        },
                        'endDate': {
                            'year': end_date.year,
                            'month': end_date.month,
                            'day': end_date.day
                        }
                    },
                    'dimensions': ['METRIC_TYPE'],
                    'metrics': [
                        'QUERIES_DIRECT',
                        'QUERIES_INDIRECT',
                        'VIEWS',
                        'ACTIONS_PHONE',
                        'ACTIONS_DIRECTIONS',
                        'ACTIONS_WEBSITE'
                    ]
                }
            )
            
            result = metrics_request.execute()
            
            # Procesar resultados
            metrics = {
                'queries_direct': 0,
                'queries_indirect': 0,
                'views': 0,
                'calls': 0,
                'directions': 0,
                'website_clicks': 0
            }
            
            if 'insights' in result:
                for insight in result['insights']:
                    metric_type = insight['metric']
                    value = int(insight.get('value', 0))
                    
                    if metric_type == 'QUERIES_DIRECT':
                        metrics['queries_direct'] = value
                    elif metric_type == 'QUERIES_INDIRECT':
                        metrics['queries_indirect'] = value
                    elif metric_type == 'VIEWS':
                        metrics['views'] = value
                    elif metric_type == 'ACTIONS_PHONE':
                        metrics['calls'] = value
                    elif metric_type == 'ACTIONS_DIRECTIONS':
                        metrics['directions'] = value
                    elif metric_type == 'ACTIONS_WEBSITE':
                        metrics['website_clicks'] = value
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error obteniendo métricas: {e}")
            return {}
    
    def get_business_profile_analysis(self, profile: Dict) -> Dict[str, Any]:
        """
        Analizar completitud del perfil
        
        Args:
            profile: Datos del perfil
            
        Returns:
            Dict con análisis
        """
        analysis = {
            'completeness_score': 0,
            'issues': [],
            'strengths': []
        }
        
        score = 0
        max_score = 100
        issues_count = 0
        
        # Verificar campos importantes
        checks = [
            ('title', "Nombre del negocio", 10),
            ('type', "Categoría del negocio", 10),
            ('description', "Descripción completa", 15),
            ('phoneNumber', "Número de teléfono", 10),
            ('websiteUrl', "Sitio web", 10),
            ('address', "Dirección completa", 15),
            ('businessHours', "Horarios de atención", 10),
            ('photos', "Fotos del negocio", 10),
        ]
        
        for field, label, points in checks:
            if field in profile and profile[field]:
                if field == 'description' and len(profile[field]) > 100:
                    score += points
                    analysis['strengths'].append(f"✅ {label}: Completa y detallada")
                elif field == 'photos' and isinstance(profile[field], list) and len(profile[field]) >= 5:
                    score += points
                    analysis['strengths'].append(f"✅ {label}: Hay suficientes fotos")
                elif field != 'description' and field != 'photos':
                    score += points
                    analysis['strengths'].append(f"✅ {label}: Completado")
                elif field == 'photos':
                    analysis['issues'].append(f"⚠️ {label}: Se recomienda agregar más fotos")
                    issues_count += 1
            else:
                analysis['issues'].append(f"❌ {label}: Falta completar")
                issues_count += 1
        
        analysis['completeness_score'] = min(score, max_score)
        analysis['issues_count'] = issues_count
        
        return analysis
