// if an array element is null then remove it from the array.
// return all non-null array items.
export function withoutNulls(arr) {
    return arr.filter((item) => item != null)
}

