import pandas as pd
import matplotlib.pyplot as plt

def pie_chart_generator(url):
    try:
        df = pd.read_csv(url)
        category_spending = df.groupby('category')['amount'].sum()

        plt.figure(figsize=(8, 8))
        plt.pie(category_spending, labels=category_spending.index, autopct='%1.1f%%', startangle=140)
        plt.title('Category Spending')
        plt.axis('equal')

        plt.savefig("PieChart.png")
        plt.show()
    except Exception as e:
        print(f"Failed to fetch data from source: {e}")

pie_chart_generator('https://drive.google.com/uc?id=1-M3ZScY9ax4vTmrLGuvOG3cqeSFFziJU')