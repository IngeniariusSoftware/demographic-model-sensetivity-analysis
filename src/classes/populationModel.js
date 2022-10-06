import {FiveYearAges} from "@/data/FiveYearAges";
import {sum} from "d3-array";

export const fertilityAgeGroups = ['20-24', '25-29', '30-34', '35-39']

export function predict(data, endYear) {
    const predictedData = []
    const stepYear = 5
    const survivalRate = getSurvivalRates(...data)
    const birthRates = getBirthRates(data[2], data[3])
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

export function getBirthRates(femaleData, maleData) {
    const womenCount = sum(fertilityAgeGroups.map(age => femaleData[age]))
    return {Female: femaleData['0-4'] / womenCount, Male: maleData['0-4'] / womenCount}
}

function getSurvivalRates(femaleYearStartData, maleYearStartData, femaleYearEndData, maleYearEndData) {
    const survivalRates = [{}, {}]
    Object.values(FiveYearAges).forEach((age, i, ages) => {
        if (i < ages.length - 1) {
            survivalRates[0][age] = getSurvivalRate(femaleYearStartData[age], femaleYearEndData[ages[i + 1]])
            survivalRates[1][age] = getSurvivalRate(maleYearStartData[age], maleYearEndData[ages[i + 1]])
        }
    })

    return {Female: survivalRates[0], Male: survivalRates[1]}
}

export function getSurvivalRate(start, end, needToRound = false) {
    const value = end / start
    return isNaN(value) ? 0.0 : needToRound ? round(value, 3) : value
}

export function round(float_number, number_of_decimals) {
    return parseFloat(float_number.toFixed(number_of_decimals))
}
