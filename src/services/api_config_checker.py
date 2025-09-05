import os
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class APIConfigChecker:
    """Verifica e valida configuração de todas as APIs"""

    def __init__(self):
        self.required_apis = {
            'ai_providers': [
                'GEMINI_API_KEY',
                'OPENAI_API_KEY',
                'GROQ_API_KEY',
                'HUGGINGFACE_API_KEY'
            ],
            'social_apis': [
                'YOUTUBE_API_KEY',
                'TWITTER_BEARER_TOKEN',
                'LINKEDIN_CLIENT_ID',
                'LINKEDIN_CLIENT_SECRET',
                'INSTAGRAM_ACCESS_TOKEN'
            ],
            'search_apis': [
                'GOOGLE_API_KEY',
                'GOOGLE_CSE_ID',
                'EXA_API_KEY',
                'TAVILY_API_KEY'
            ],
            'database': [
                'SUPABASE_URL',
                'SUPABASE_KEY'
            ]
        }

    def check_all_apis(self) -> Dict[str, any]:
        """Verifica todas as configurações de API"""
        results = {
            'status': 'checking',
            'categories': {},
            'missing_critical': [],
            'missing_optional': [],
            'health_score': 0
        }

        total_apis = 0
        configured_apis = 0

        for category, apis in self.required_apis.items():
            category_result = {
                'status': 'ok',
                'configured': [],
                'missing': [],
                'score': 0
            }

            for api_key in apis:
                total_apis += 1
                if os.getenv(api_key):
                    category_result['configured'].append(api_key)
                    configured_apis += 1
                else:
                    category_result['missing'].append(api_key)

                    # Classificar como crítico ou opcional
                    if api_key in ['GEMINI_API_KEY', 'GOOGLE_API_KEY', 'SUPABASE_URL']:
                        results['missing_critical'].append(api_key)
                    else:
                        results['missing_optional'].append(api_key)

            category_result['score'] = len(category_result['configured']) / len(apis) * 100
            if category_result['missing']:
                category_result['status'] = 'partial' if category_result['configured'] else 'missing'

            results['categories'][category] = category_result

        # Calcular score geral
        results['health_score'] = (configured_apis / total_apis) * 100 if total_apis > 0 else 0
        results['status'] = self._determine_overall_status(results)

        return results

    def _determine_overall_status(self, results: Dict) -> str:
        """Determina status geral baseado nas configurações"""
        if results['missing_critical']:
            return 'critical'
        elif results['health_score'] >= 80:
            return 'excellent'
        elif results['health_score'] >= 60:
            return 'good'
        elif results['health_score'] >= 40:
            return 'fair'
        else:
            return 'poor'

    def get_setup_instructions(self) -> Dict[str, str]:
        """Retorna instruções de configuração para APIs ausentes"""
        check_result = self.check_all_apis()
        instructions = {}

        for category, data in check_result['categories'].items():
            if data['missing']:
                instructions[category] = self._get_category_instructions(category, data['missing'])

        return instructions

    def _get_category_instructions(self, category: str, missing_apis: List[str]) -> str:
        """Gera instruções específicas para categoria"""
        instructions_map = {
            'ai_providers': "Configure provedores de IA em https://aistudio.google.com/app/apikey (Gemini) ou https://platform.openai.com/api-keys (OpenAI)",
            'social_apis': "Configure APIs sociais: YouTube (console.developers.google.com), Twitter (developer.twitter.com)",
            'search_apis': "Configure APIs de busca: Google Custom Search (console.developers.google.com/apis/api/customsearch.googleapis.com)",
            'database': "Configure Supabase em https://supabase.com/dashboard/projects"
        }

        return instructions_map.get(category, "Verifique a documentação da API correspondente")