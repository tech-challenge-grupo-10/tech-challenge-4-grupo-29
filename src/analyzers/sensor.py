class SensorAnalyzer:
    """Classe responsável por avaliar dados fisiológicos."""
    
    def analyze(self, sys, dia, spo2):
        """
        Avalia a pressão arterial e SpO2.
        Lógica de alerta: PA > 140/90 (14/9) ou SpO2 < 94% em repouso.
        """
        risks = []
        is_stressed = False
        
        # Análise Pressão Arterial
        if sys > 140 or dia > 90:
            risks.append("⚠️ ALERTA: Pressão Arterial elevada (> 140/90 mmHg). Possível indicador de estresse agudo ou hipertensão.")
            is_stressed = True
        elif sys < 90 or dia < 60:
            risks.append("⚠️ ALERTA: Pressão Arterial baixa (< 90/60 mmHg).")
        else:
            risks.append("✅ Pressão Arterial dentro dos padrões normais.")
            
        # Análise SpO2
        if spo2 < 94:
            risks.append("⚠️ ALERTA: Saturação de Oxigênio (SpO2) perigosamente baixa (< 94%). Possível indicador de ansiedade severa (hiperventilação/hipoventilação) ou problema fisiológico.")
            is_stressed = True
        else:
            risks.append("✅ Saturação de Oxigênio normal.")
            
        risk_level = "Alto Risco de Estresse/Ansiedade Fisiológica" if is_stressed else "Padrão Fisiológico Estável"
        
        return {
            "risk_level": risk_level,
            "details": "\n".join(risks),
            "sys": sys,
            "dia": dia,
            "spo2": spo2
        }
