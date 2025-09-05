#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Selenium Health Checker
Verificador de saúde do Selenium e Chrome
"""

import logging
import subprocess
import glob
import os  # Importado para os.path.exists
from pathlib import Path

logger = logging.getLogger(__name__)

class SeleniumChecker:
    """Verificador de configuração do Selenium"""

    def __init__(self):
        self.chrome_paths = []
        self.chromedriver_available = False

    def check_chrome_installation(self) -> bool:
        """Verifica se o Chrome está instalado"""
        # Verifica se o Chrome está instalado
        chrome_paths = [
            "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/opt/google/chrome/chrome",
            "/nix/store/*/bin/google-chrome-stable",
            "/nix/store/*/bin/chromium"
        ]

        chrome_available = False

        # Verifica caminhos diretos
        for path in chrome_paths:
            if '*' in path:
                # Para caminhos do Nix com wildcard
                import glob
                matching_paths = glob.glob(path)
                if matching_paths and any(os.path.exists(p) for p in matching_paths):
                    self.chrome_paths.extend(p for p in matching_paths if os.path.exists(p))
                    chrome_available = True
                    logger.info(f"✅ Chrome encontrado no Nix (wildcard): {self.chrome_paths}")
                    break
            elif os.path.exists(path):
                self.chrome_paths.append(path)
                logger.info(f"✅ Chrome encontrado: {path}")
                chrome_available = True
                break

        if not chrome_available:
            # Tenta encontrar via comando
            try:
                commands = ['google-chrome', 'chromium', 'google-chrome-stable']
                for cmd in commands:
                    result = subprocess.run(['which', cmd],
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        self.chrome_paths.append(result.stdout.strip())
                        logger.info(f"✅ Chrome encontrado via which: {result.stdout.strip()}")
                        chrome_available = True
                        break
            except Exception as e:
                logger.warning(f"⚠️ Erro ao tentar encontrar Chrome via 'which': {e}")


        if not chrome_available:
            logger.error("❌ Chrome não encontrado")
        return chrome_available


    def check_chromedriver(self) -> bool:
        """Verifica se o ChromeDriver está disponível"""
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            driver_path = ChromeDriverManager().install()
            if Path(driver_path).exists():
                self.chromedriver_available = True
                logger.info(f"✅ ChromeDriver disponível: {driver_path}")
                return True
        except Exception as e:
            logger.warning(f"⚠️ ChromeDriverManager erro: {e}")

        # Verifica se chromedriver está no PATH
        try:
            result = subprocess.run(['which', 'chromedriver'],
                                 capture_output=True, text=True)
            if result.returncode == 0:
                self.chromedriver_available = True
                logger.info(f"✅ ChromeDriver no PATH: {result.stdout.strip()}")
                return True
        except Exception:
            pass

        logger.error("❌ ChromeDriver não disponível")
        return False

    def get_best_chrome_path(self) -> str:
        """Retorna o melhor caminho do Chrome encontrado"""
        if not self.chrome_paths:
            return None

        # Prioriza google-chrome-stable
        for path in self.chrome_paths:
            if 'google-chrome-stable' in path:
                return path

        # Depois google-chrome
        for path in self.chrome_paths:
            if 'google-chrome' in path and 'stable' not in path:
                return path

        # Qualquer um disponível
        return self.chrome_paths[0]

    def full_check(self) -> dict:
        """Executa verificação completa"""
        results = {
            'chrome_available': self.check_chrome_installation(),
            'chromedriver_available': self.check_chromedriver(),
            'chrome_paths': self.chrome_paths,
            'best_chrome_path': self.get_best_chrome_path(),
            'selenium_ready': False
        }

        results['selenium_ready'] = (
            results['chrome_available'] and
            results['chromedriver_available']
        )

        if results['selenium_ready']:
            logger.info("✅ Selenium totalmente configurado e pronto")
        else:
            logger.error("❌ Selenium não está pronto")

        return results

# Instância global
selenium_checker = SeleniumChecker()

# Executa verificação na importação
if __name__ != "__main__":
    check_results = selenium_checker.full_check()