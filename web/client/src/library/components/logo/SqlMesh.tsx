import React, { memo } from 'react'
import { type ColorScheme, EnumColorScheme } from '~/context/theme'

interface PropsLogoSqlMesh extends React.SVGAttributes<SVGAElement> {
  mode: ColorScheme
}

function LogoSqlMesh({
  style,
  className,
  mode,
}: PropsLogoSqlMesh): JSX.Element {
  const fill =
    mode === EnumColorScheme.Light
      ? 'var(--color-primary-800)'
      : 'var(--color-primary-600)'
  const strokeDarker =
    mode === EnumColorScheme.Light
      ? 'var(--color-primary-400)'
      : 'var(--color-primary-200)'
  const strokeLighter =
    mode === EnumColorScheme.Light
      ? 'var(--color-primary-600)'
      : 'var(--color-primary-400)'

  return (
    <svg
      style={style}
      className={className}
      viewBox="0 0 240 72"
      xmlns="http://www.w3.org/2000/svg"
    >
      <title>SQLMesh logo</title>
      <path
        d="M60 41V33.2222C60 20.9492 49.2548 11 36 11C22.7452 11 12 20.9492 12 33.2222V41"
        stroke={strokeDarker}
        strokeWidth="5"
      />
      <path
        d="M60 41V46.1852C60 54.3672 52.8366 61 44 61C35.1634 61 28 54.3672 28 46.1852V41"
        stroke={strokeDarker}
        strokeWidth="5"
      />
      <path
        d="M60 41V43.5926C60 47.6836 56.4183 51 52 51C47.5817 51 44 47.6836 44 43.5926V41"
        stroke={strokeLighter}
        strokeWidth="5"
      />
      <path
        d="M44 41V35.8148C44 27.6328 36.8366 21 28 21C19.1634 21 12 27.6328 12 35.8148V41"
        stroke={strokeLighter}
        strokeWidth="5"
      />
      <circle
        cx="60"
        cy="41"
        r="6"
        fill={fill}
      />
      <circle
        cx="44"
        cy="41"
        r="6"
        fill={fill}
      />
      <circle
        cx="28"
        cy="41"
        r="6"
        fill={fill}
      />
      <circle
        cx="12"
        cy="41"
        r="6"
        fill={fill}
      />
      <path
        d="M94.512 29.272C93.936 26.5 91.632 22.936 85.872 22.936C81.156 22.936 77.448 26.536 77.448 30.532C77.448 34.348 80.04 36.724 83.676 37.516L87.312 38.308C89.868 38.848 91.128 40.432 91.128 42.268C91.128 44.5 89.4 46.336 85.872 46.336C82.02 46.336 80.004 43.708 79.752 40.864L76.368 41.944C76.836 45.58 79.752 49.54 85.908 49.54C91.344 49.54 94.728 45.94 94.728 41.98C94.728 38.416 92.352 35.752 88.104 34.816L84.288 33.988C82.128 33.52 81.012 32.116 81.012 30.28C81.012 27.904 83.064 26.032 85.944 26.032C89.508 26.032 91.056 28.552 91.344 30.388L94.512 29.272ZM97.7841 36.22C97.7841 44.752 104.192 49.54 110.6 49.54C112.94 49.54 115.28 48.928 117.296 47.704L120.392 51.124L122.804 49L119.816 45.652C121.976 43.42 123.416 40.252 123.416 36.22C123.416 27.688 117.008 22.936 110.6 22.936C104.192 22.936 97.7841 27.688 97.7841 36.22ZM101.384 36.22C101.384 29.56 105.848 26.176 110.6 26.176C115.352 26.176 119.816 29.56 119.816 36.22C119.816 39.172 118.916 41.476 117.548 43.132L113.084 38.092L110.636 40.216L115.064 45.184C113.696 45.94 112.184 46.3 110.6 46.3C105.848 46.3 101.384 42.88 101.384 36.22ZM143.855 49V45.688H131.795V23.476H128.267V49H143.855Z"
        className="fill-prose"
      />
      <path
        d="M178.68 49V23.476H170.868L164.208 40.72L157.188 23.476H149.772V49H155.172V32.296L161.832 49H166.44L173.1 32.08V49H178.68ZM187.829 37.912C187.937 36.58 189.089 34.888 191.393 34.888C193.985 34.888 194.921 36.544 194.993 37.912H187.829ZM195.389 42.556C194.885 43.96 193.769 44.896 191.789 44.896C189.665 44.896 187.829 43.456 187.721 41.44H200.177C200.213 41.332 200.285 40.504 200.285 39.748C200.285 33.988 196.865 30.568 191.321 30.568C186.677 30.568 182.393 34.24 182.393 40C182.393 46.012 186.785 49.54 191.717 49.54C196.253 49.54 199.097 46.948 199.961 43.852L195.389 42.556ZM202.323 43.924C202.467 45.904 204.267 49.54 209.883 49.54C214.671 49.54 217.011 46.552 217.011 43.492C217.011 40.864 215.211 38.632 211.503 37.876L209.127 37.408C208.335 37.264 207.723 36.832 207.723 36.076C207.723 35.14 208.623 34.528 209.667 34.528C211.323 34.528 212.079 35.536 212.223 36.724L216.759 35.896C216.579 33.808 214.779 30.568 209.595 30.568C205.599 30.568 202.719 33.232 202.719 36.508C202.719 39.028 204.231 41.188 208.047 42.016L210.099 42.484C211.431 42.772 211.863 43.312 211.863 43.96C211.863 44.752 211.179 45.508 209.775 45.508C207.903 45.508 207.039 44.32 206.967 43.096L202.323 43.924ZM226.04 38.488C226.148 36.832 227.264 35.608 228.992 35.608C230.972 35.608 231.908 36.94 231.908 38.704V49H237.38V37.768C237.38 33.844 235.292 30.64 230.612 30.64C229.028 30.64 227.156 31.144 226.04 32.26V22.936H220.568V49H226.04V38.488Z"
        className="fill-prose"
      />
    </svg>
  )
}

export default memo(LogoSqlMesh)
