# -*- coding: utf-8 -*-
"""old_pop.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1jY5QqmjTfOKyPcHKWicZRgoXtYKbU2_L

# **Введение**

Мой основной текущий проект связан с авторынком, но найти интересные актуальные данные сложно, они платные, а разобраться с парсингом auto.ru я не успела. Данные об автомобилях с Kaggle, которые меня заинтересовали, были или устаревшими, или сгенерированными, а мне хотелось поработать с настоящим датасетом. В итоге я нашла большой датасет [Крупные города России: объединенные данные по основным социально-экономическим показателям за 1985-2019 гг](https://data.rcsi.science/data-catalog/datasets/187/). и решила посмотреть, что в нем есть. У долго сопоставляла разные параметры (например, количество метров жилплощади и рождаемости), выдвигая разные гипотезы, но нигде не было убедительных корелляций. Наконец, я решила проверить зависимость между количеством врачей и медсестер и количеством пожилого населения (по моей гипотезе такая связь должна быть, ведь от качества медицинского обслуживания отчасти зависит продолжительности жизни).

Для оценки качества модели я выбрала метрики средней квадратичной ошибки (MSE) и коэффициента детерминации (R²). MSE позволяет оценить, насколько точно модель предсказывает реальные значения, а R² показывает, какая доля общей вариации данных объясняется моделью. Эти метрики помогают определить, насколько модель адекватно описывает зависимость между количеством врачей, медсестер и пожилым населением в разных регионах.

# **EDA**
"""

import pandas as pd

df = pd.read_csv('Russia.csv')

# Сначала надо посмотреть, какие в принципе данные есть в этом датасете
print()
print(df.columns)

import pandas as pd

df = pd.read_csv('Russia.csv')
relevant_cols = ['region', 'year', 'population', 'doctors', 'nurses', 'doctors_per10', 'nurses_per10', 'pop_old', 'polycl_visits', 'hospital_beds']
data = df[relevant_cols]
print(relevant_cols)

data.info()

data.isnull().sum()

data[['doctors', 'nurses']].describe()

# Предыдущий этап выявил большой разброс между значениями min и max, я хочу проверить, о каких регионах идет речь. Зная административно-терроториальное деление России, я могу предположить, что разрыв в реальности может быть очень большим.

if 'upper_bound_doctors' not in locals() or 'upper_bound_nurses' not in locals():
    # Если переменные отсутствуют, вычисляем их заново
    Q1_doctors = data['doctors'].quantile(0.25)
    Q3_doctors = data['doctors'].quantile(0.75)
    IQR_doctors = Q3_doctors - Q1_doctors
    upper_bound_doctors = Q3_doctors + 1.5 * IQR_doctors

    Q1_nurses = data['nurses'].quantile(0.25)
    Q3_nurses = data['nurses'].quantile(0.75)
    IQR_nurses = Q3_nurses - Q1_nurses
    upper_bound_nurses = Q3_nurses + 1.5 * IQR_nurses

# Выделяем выбросы
outliers_doctors = data[data['doctors'] > upper_bound_doctors]
outliers_nurses = data[data['nurses'] > upper_bound_nurses]

# Выводим результаты
print("Выбросы по количеству врачей:")
print(outliers_doctors[['region', 'doctors']])

print("\nВыбросы по количеству медсестер:")
print(outliers_nurses[['region', 'nurses']])

# Вижу, что большие значения в более населенных районах, хочу посмотреть корелляцию между населением и количеством врачей, медсестер, чтобы проверить, насколько реалистичны данные.

required_columns = ['population', 'doctors', 'nurses']
missing_columns = [col for col in required_columns if col not in data.columns]

if missing_columns:
    raise ValueError(f"Отсутствуют необходимые колонки: {missing_columns}")

# Убираем строки с NaN, если есть
data = data.dropna(subset=required_columns)

# Считаем корреляцию
correlation_population_doctors = data['population'].corr(data['doctors'])
correlation_population_nurses = data['population'].corr(data['nurses'])

print(f"Корреляция между населением и количеством врачей: {correlation_population_doctors}")
print(f"Корреляция между населением и количеством медсестер: {correlation_population_nurses}")

# Корелляция между населением и количеством врачей, медсестер достаточно высокая, так что я считаю данные реалистичными, разрыв между min и max реалистичен. Перехожу к следующему этапу: визуализация изменения количества врачей, медсестер по годам.
import matplotlib.pyplot as plt
import seaborn as sns

yearly_data = data.groupby('year').agg({'doctors': 'mean', 'nurses': 'mean'}).reset_index()

plt.figure(figsize=(12, 6))
sns.lineplot(x='year', y='doctors', data=yearly_data, label='Врачи')
sns.lineplot(x='year', y='nurses', data=yearly_data, label='Медсестры')
plt.title('Среднее количество врачей и медсестер по годам')
plt.xlabel('Год')
plt.ylabel('Среднее количество')
plt.legend()
plt.show()

yearly_data = data.groupby('year').agg({'doctors': 'mean', 'nurses': 'mean'}).reset_index()

plt.figure(figsize=(12, 6))
sns.lineplot(x='year', y='doctors', data=yearly_data, label='Врачи')
sns.lineplot(x='year', y='nurses', data=yearly_data, label='Медсестры')
plt.title('Среднее количество врачей и медсестер по годам')
plt.xlabel('Год')
plt.ylabel('Среднее количество')
plt.legend()
plt.show()

# Хочу еще посмотреть тренды измнения количества врачей, медсестер на 10 тыс населения.
normalized_data = data.groupby('year').agg({'doctors_per10': 'mean', 'nurses_per10': 'mean'}).reset_index()

plt.figure(figsize=(12, 6))
sns.lineplot(x='year', y='doctors_per10', data=normalized_data, label='Врачи на 10,000')
sns.lineplot(x='year', y='nurses_per10', data=normalized_data, label='Медсестры на 10,000')
plt.title('Среднее количество врачей и медсестер на 10,000 населения по годам')
plt.xlabel('Год')
plt.ylabel('Среднее количество на 10,000 населения')
plt.legend()
plt.show()

"""# **Построение безлайна**"""

# Я хочу посмотреть, как количество врачей, медсестер влияет на количество пожилого населения при помощи линейной регрессии (подозреваю линейную зависимость).


X = data[['doctors', 'nurses', 'doctors_per10', 'nurses_per10']]
y = data['pop_old']  # Целевая переменная - пожилое население.


data_cleaned = pd.concat([X, y], axis=1)
data_cleaned = data_cleaned.dropna()

X_cleaned = data_cleaned.drop(columns=['pop_old'])
y_cleaned = data_cleaned['pop_old']

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X_cleaned, y_cleaned, test_size=0.2, random_state=42)

from sklearn.linear_model import LinearRegression
model = LinearRegression()

model.fit(X_train, y_train)

y_pred = model.predict(X_test)


# Для оценки модели я буду использоваться cреднеквадратичную ошибку (MSE) и коэффициент детерминации (R²).
from sklearn.metrics import mean_squared_error, r2_score
mse = mean_squared_error(y_test, y_pred) # Среднеквадратичная ошибка
r2 = r2_score(y_test, y_pred)  # Коэффициент детерминации

print(f"Коэффициенты регрессии: {model.coef_}")
print(f"Смещение (интерсепт): {model.intercept_}")
print(f"Среднеквадратичная ошибка (MSE): {mse}")
print(f"Коэффициент детерминации (R²): {r2}")

"""# **Заключение**

Модель линейной регрессии подтверждает гипотезу, что связь между количеством пожилого населения и количеством врачей, медсестер существует. Однако, скорее всего влияние оказывают и другие факторы, которые тоже можно исследовать (уровень дохода, доступ к медицинским услугам или экологические условия).

R² = 0.93. Это указывает на то, что модель объясняет 93% вариации в численности пожилого населения. Это высокий показатель, который свидетельствует о хорошей предсказательной способности модели. Среднеквадратичная ошибка (MSE) = 351.54. Это указывает на относительно небольшую разницу между предсказанными и реальными значениями.
"""