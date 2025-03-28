import pandas as pd
import os

class CompanySocialParameters:
    def __init__(self):
        self.parameters = {
            'company1': {'a': 0.91, 'b': 0.55, 'c': 0.6, 'd': 2.6},
            'company2': {'a': 0.82, 'b': 0.40, 'c': 0.8, 'd': 2.8},
            'company3': {'a': 0.85, 'b': 0.16, 'c': 0.2, 'd': 0.35}
        }
    
    def get_factors(self):
        return {company: sum(params.values()) for company, params in self.parameters.items()}

class JusticeScoreCalculator:
    def __init__(self, csv_filename, company_social_parameters):
        csv_file = os.path.join(os.path.dirname(__file__), csv_filename)
        self.df = pd.read_csv(csv_file)
        self.df['date'] = pd.to_datetime(self.df['date'], format='mixed', dayfirst=False)
        self.df['date'] = self.df['date'].dt.strftime('%d-%m-%Y')
        self.alphaFactors = company_social_parameters.get_factors()
        self.beta1, self.beta2, self.beta3 = 0, 0, 0
    
    def determine_winners_share(self):
        for _, row in self.df.iterrows():
            supplied_capacities = {
                'company1': row['company1_supplied_capacity'],
                'company2': row['company2_supplied_capacity'],
                'company3': row['company3_supplied_capacity']
            }
            demand = row['demand']
            b1= supplied_capacities['company1'] / demand
            b2= supplied_capacities['company2'] / demand
            b3= supplied_capacities['company3'] / demand
            summ = b1 + b2 + b3
            if (summ < 1):
                minn = min(b1,b2,b3)
                remainn= 1-summ
                if b1 == minn:
                    b1 += remainn
                elif b2 == minn:
                    b2 += remainn
                else:
                    b3 += remainn

            self.beta1 += b1
            self.beta2 += b2
            self.beta3 += b3
    
    def calculate_justice_score(self):
        self.determine_winners_share()
        system_score = (self.alphaFactors['company1'] * self.beta1) + (self.alphaFactors['company2'] * self.beta2) + (self.alphaFactors['company3'] * self.beta3)
        return {
            'Beta1': round(self.beta1, 3),
            'Alpha1': round(self.alphaFactors['company1'], 3),
            'Beta2': round(self.beta2, 3),
            'Alpha2': round(self.alphaFactors['company2'], 3),
            'Beta3': round(self.beta3, 3),
            'Alpha3': round(self.alphaFactors['company3'], 3),
            'SystemScore': round(system_score, 3)
        }

if __name__ == "__main__":
    company_parameters = CompanySocialParameters()
    calculator = JusticeScoreCalculator('market_modified.csv', company_parameters)
    result = calculator.calculate_justice_score()
    print(result)