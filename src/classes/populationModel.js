import {FiveYearAges} from "@/data/FiveYearAges";
import {sum} from "d3-array";

export const fertilityAgeGroups = ['20-24', '25-29', '30-34', '35-39']

export function predict(data, endYear, fertility, female_percentage, femaleSurvivalRates, maleSurvivalRates) {
    const predictedData = []
    const stepYear = 5
    const survivalRate = getSurvivalRates(data[0], data[1], data[2], data[3], femaleSurvivalRates, maleSurvivalRates)
    const birthRates = getBirthRates(data[2], data[3], fertility, female_percentage)
    const startYear = data[2].year
    const ageGroups = Object.values(FiveYearAges)
    const survivedAgeGroups = Object.values(FiveYearAges).slice(1)
    let lastWomenData = data[2]
    let lastMenData = data[3]
    for (let year = startYear + stepYear; year <= endYear; year += stepYear) {
        const womenCount = sum(fertilityAgeGroups.map(age => lastWomenData[age]))
        const currentWomenData = {'0-4': Math.round(womenCount * birthRates.Female), sex: 'Female', year: year}
        const currentMenData = {'0-4': Math.round(womenCount * birthRates.Male), sex: 'Male', year: year}
        survivedAgeGroups.forEach((age, i) => {
            const lastAgeGroup = ageGroups[i]
            currentWomenData[age] = Math.round(lastWomenData[lastAgeGroup] * survivalRate.Female[lastAgeGroup])
            currentMenData[age] = Math.round(lastMenData[lastAgeGroup] * survivalRate.Male[lastAgeGroup])
        })
        predictedData.push(currentWomenData)
        predictedData.push(currentMenData)
        lastWomenData = structuredClone(currentWomenData)
        lastMenData = structuredClone(currentMenData)
    }
    return predictedData
}

export function getBirthRates(femaleData, maleData, fertility, female_percentage) {
    const womenCount = sum(fertilityAgeGroups.map(age => femaleData[age]))
    fertility = fertility ? fertility / fertilityAgeGroups.length : (femaleData['0-4'] + maleData['0-4']) / womenCount
    female_percentage = female_percentage ? female_percentage : femaleData['0-4'] / (femaleData['0-4'] + maleData['0-4'])
    return {Female: fertility * female_percentage, Male: fertility * (1 - female_percentage)}
}

function getSurvivalRates(femaleYearStartData, maleYearStartData, femaleYearEndData, maleYearEndData, femaleSurvivalRates, maleSurvivalRates) {
    const survivalRates = [{}, {}]
    Object.values(FiveYearAges).forEach((age, i, ages) => {
        if (i < ages.length - 1) {
            survivalRates[0][age] = getSurvivalRate(femaleYearStartData[age], femaleYearEndData[ages[i + 1]])
            survivalRates[1][age] = getSurvivalRate(maleYearStartData[age], maleYearEndData[ages[i + 1]])
        }
    })

    if (femaleSurvivalRates) {
        Object.entries(([age, value]) => {
            survivalRates[0][age] = value
        })
    }

    if (maleSurvivalRates) {
        Object.entries(([age, value]) => {
            survivalRates[1][age] = value
        })
    }

    return {Female: survivalRates[0], Male: survivalRates[1]}
}

export function getSurvivalRate(start, end, needToRound = false) {
    const value = end / start
    return isFinite(value) ? needToRound ? round(value, 3) : value : 0.0
}

export function round(float_number, number_of_decimals) {
    return parseFloat(float_number.toFixed(number_of_decimals))
}
