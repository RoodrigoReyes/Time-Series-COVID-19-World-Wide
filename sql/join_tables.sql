select cp.country,
    cp.lat,
    cp.long,
    cp.fecha,
    cp.total as posit_total,
    cp.day_total as posit_day,
    cd.total as deaths_total,
    cd.day_total as deaths_day,
    cr.total as recov_total,
    cr.day_total as recov_day,
    cv.total as vaccine_total,
    cv.day_total as vaccine_day
from covid.positives cp
    left join covid.deaths cd on cd.country = cp.country
    and cd.fecha = cp.fecha
    left join covid.recovered cr on cr.country = cp.country
    and cr.fecha = cp.fecha
    left join covid.vaccines cv on cv.country = cp.country
    and cv.fecha = cp.fecha
order by cp.country,
    cp.fecha;